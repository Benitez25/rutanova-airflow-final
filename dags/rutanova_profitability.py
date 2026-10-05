# DAG definition has no network calls, credentials or business logic at parse time.
from datetime import timedelta
from pathlib import Path
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.task_group import TaskGroup
from src.runtime import ingest_api, ingest_csv, load_warehouse, dbt_build, export_report

def csv_arrived():
    p = Path('/opt/airflow/inbox/delivery_costs.csv')
    return p.is_file() and p.stat().st_size > 0

with DAG(
    dag_id='rutanova_profitability',
    description='Two sources -> MinIO -> Snowflake -> dbt -> city profitability',
    start_date=pendulum.datetime(2026,1,1,tz='America/Lima'),
    schedule='0 7 * * *', catchup=False, max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
    default_args={'owner':'rutanova_data_team','retries':2,'retry_delay':timedelta(minutes=1),
                  'retry_exponential_backoff':True,'max_retry_delay':timedelta(minutes=5),
                  'execution_timeout':timedelta(minutes=10)},
    tags=['final_project','snowflake','dbt','logistics'],
    doc_md='''
    # RutaNova: rentabilidad de pedidos
    Cada día a las 07:00 de Lima se espera el CSV de reparto, se consulta la API
    de pedidos y se archivan ambas fuentes en MinIO. Se valida la cobertura de
    costos antes de cargar un snapshot atómico en Snowflake. dbt construye staging,
    detalle de rentabilidad y un mart por fecha/ciudad, ejecutando sus tests.
    Owner: rutanova_data_team. Las fuentes son simuladas explícitamente.
    El snapshot es completo y las cancelaciones se excluyen de los indicadores.
    XCom transporta claves de objetos y conteos; nunca datasets ni credenciales.
    '''
) as dag:
    with TaskGroup('ingestion') as ingestion:
        wait_csv = PythonSensor(task_id='wait_delivery_csv', python_callable=csv_arrived,
                                mode='reschedule', poke_interval=30, timeout=600, retries=0)
        api = PythonOperator(task_id='archive_api', python_callable=ingest_api,
                             op_kwargs={'run_id':'{{ run_id }}'})
        csv = PythonOperator(task_id='archive_csv', python_callable=ingest_csv,
                             op_kwargs={'run_id':'{{ run_id }}'})
        wait_csv >> csv
    with TaskGroup('warehouse') as warehouse:
        load = PythonOperator(task_id='load_atomic_snapshot', python_callable=load_warehouse,
                              op_kwargs={'keys':[api.output,csv.output], 'run_id':'{{ run_id }}'})
    with TaskGroup('transformation') as transformation:
        build = PythonOperator(task_id='dbt_build', python_callable=dbt_build,
                               execution_timeout=timedelta(minutes=20))
    report = PythonOperator(task_id='export_report', python_callable=export_report)
    ingestion >> warehouse >> transformation >> report
