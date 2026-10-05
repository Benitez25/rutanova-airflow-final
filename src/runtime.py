"""Runtime integration. Connection values are resolved only during task execution."""
import csv
import io
import json
import logging
import os
import re
import subprocess
from pathlib import Path
from airflow.hooks.base import BaseHook
from src.business import validate_orders, validate_costs, reconcile
LOG = logging.getLogger(__name__)
BUCKET = 'rutanova-raw'

def storage():
    import boto3
    from botocore.config import Config
    c = BaseHook.get_connection('rutanova_minio')
    return boto3.client('s3', endpoint_url=c.extra_dejson['endpoint_url'],
                        aws_access_key_id=c.login, aws_secret_access_key=c.password,
                        region_name='us-east-1', config=Config(signature_version='s3v4',
                        s3={'addressing_style':'path'}, retries={'max_attempts':3, 'mode':'standard'}))

def prefix(run_id):
    import hashlib
    return 'snapshots/' + hashlib.sha256(run_id.encode()).hexdigest()[:20]

def ingest_api(run_id):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    c = BaseHook.get_connection('rutanova_api')
    with requests.Session() as session:
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504], allowed_methods=['GET'])
        session.mount('http://', HTTPAdapter(max_retries=retry))
        session.mount('https://', HTTPAdapter(max_retries=retry))
        try:
            response = session.get(c.host.rstrip('/') + '/orders', timeout=(3.05,30))
            response.raise_for_status()
            content = response.content
            validate_orders(response.json())
        except (requests.RequestException, ValueError) as exc:
            raise RuntimeError('Orders API failed or returned invalid data') from exc
    key = prefix(run_id) + '/orders.json'
    storage().put_object(Bucket=BUCKET, Key=key, Body=content, ContentType='application/json')
    return key

def ingest_csv(run_id):
    content = Path('/opt/airflow/inbox/delivery_costs.csv').read_bytes()
    validate_costs(content.decode('utf-8-sig'))
    key = prefix(run_id) + '/delivery_costs.csv'
    storage().put_object(Bucket=BUCKET, Key=key, Body=content, ContentType='text/csv')
    return key

def read_inputs(keys):
    client = storage()
    raw = [client.get_object(Bucket=BUCKET, Key=k)['Body'].read() for k in keys]
    return validate_orders(json.loads(raw[0])), validate_costs(raw[1].decode('utf-8-sig'))

def sf_settings():
    c = BaseHook.get_connection('rutanova_snowflake')
    x = c.extra_dejson
    params = {k:x[k] for k in ['account','database','warehouse','role']}
    params.update(user=c.login, schema='RAW', login_timeout=30, network_timeout=60,
                  session_parameters={'QUERY_TAG':'rutanova_airflow'})
    if x.get('auth') == 'keypair':
        params['private_key_file'] = x['private_key_path']
    else:
        params['password'] = c.password
    return params

def snowflake():
    import snowflake.connector
    return snowflake.connector.connect(**sf_settings())

def sf_identifier(value):
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*', value):
        raise ValueError('Snowflake names must use uppercase letters, digits or underscores')
    return value

def load_warehouse(keys, run_id):
    """Atomic full snapshot: retries cannot append duplicates or publish half a snapshot.

    The lab API contract is a COMPLETE snapshot. For incremental sources, replace this
    transaction with an explicit MERGE/watermark contract before going to production.
    """
    orders, costs = read_inputs(keys)
    counts = reconcile(orders, costs)
    with snowflake() as conn:
        with conn.cursor() as cur:
            # DDL must be outside the transaction: Snowflake DDL implicitly commits.
            cur.execute('CREATE TABLE IF NOT EXISTS RAW.ORDERS (ORDER_ID VARCHAR, ORDER_DATE DATE, CITY VARCHAR, REVENUE NUMBER(14,2), PRODUCT_COST NUMBER(14,2), STATUS VARCHAR, SOURCE_KEY VARCHAR, RUN_ID VARCHAR, INGESTED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP())')
            cur.execute('CREATE TABLE IF NOT EXISTS RAW.DELIVERY_COSTS (ORDER_ID VARCHAR, DELIVERY_COST NUMBER(14,2), DELIVERY_DATE DATE, SOURCE_KEY VARCHAR, RUN_ID VARCHAR, INGESTED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP())')
            cur.execute('CREATE TABLE IF NOT EXISTS RAW.PIPELINE_AUDIT (RUN_ID VARCHAR, ORDERS_COUNT NUMBER, COSTS_COUNT NUMBER, LOADED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP())')
            cur.execute('BEGIN')
            try:
                cur.execute('DELETE FROM RAW.ORDERS')
                cur.execute('DELETE FROM RAW.DELIVERY_COSTS')
                cur.executemany('INSERT INTO RAW.ORDERS (ORDER_ID,ORDER_DATE,CITY,REVENUE,PRODUCT_COST,STATUS,SOURCE_KEY,RUN_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                    [(r['order_id'],r['order_date'],r['city'],r['revenue'],r['product_cost'],r['status'],keys[0],run_id) for r in orders])
                cur.executemany('INSERT INTO RAW.DELIVERY_COSTS (ORDER_ID,DELIVERY_COST,DELIVERY_DATE,SOURCE_KEY,RUN_ID) VALUES (%s,%s,%s,%s,%s)',
                    [(r['order_id'],r['delivery_cost'],r['delivery_date'],keys[1],run_id) for r in costs])
                cur.execute('DELETE FROM RAW.PIPELINE_AUDIT WHERE RUN_ID = %s', (run_id,))
                cur.execute('INSERT INTO RAW.PIPELINE_AUDIT (RUN_ID,ORDERS_COUNT,COSTS_COUNT) VALUES (%s,%s,%s)', (run_id,counts['orders'],counts['costs']))
                cur.execute('COMMIT')
            except Exception:
                cur.execute('ROLLBACK')
                raise
    LOG.info('Atomic snapshot loaded: %s', counts)
    return counts

def dbt_build():
    """dbt executed through a subprocess without templating secrets into logs/XCom."""
    p = sf_settings()
    child_env = os.environ.copy()
    mapping = {'account':'DBT_SF_ACCOUNT','user':'DBT_SF_USER','database':'DBT_SF_DATABASE',
               'warehouse':'DBT_SF_WAREHOUSE','role':'DBT_SF_ROLE'}
    child_env.update({env:str(p[key]) for key,env in mapping.items()})
    child_env['DBT_SF_TARGET'] = 'keypair' if 'private_key_file' in p else 'password'
    child_env['DBT_SF_KEY_PATH'] = p.get('private_key_file','')
    child_env['DBT_ENV_SECRET_SF_PASSWORD'] = p.get('password') or ''
    subprocess.run(['/opt/airflow/dbt-venv/bin/dbt','build','--project-dir','/opt/airflow/dbt',
                    '--profiles-dir','/opt/airflow/dbt'], env=child_env, check=True)

def export_report():
    with snowflake() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM ANALYTICS.MART_CITY_PROFITABILITY ORDER BY ORDER_DATE,CITY')
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            if not rows:
                raise RuntimeError('Final mart is empty')
    path = Path('/opt/airflow/reports/city_profitability.csv')
    temp = path.with_suffix('.tmp')
    with temp.open('w',newline='',encoding='utf-8') as f:
        writer = csv.writer(f);writer.writerow(cols);writer.writerows(rows)
    temp.replace(path)
    return {'rows':len(rows),'report':'reports/city_profitability.csv'}
