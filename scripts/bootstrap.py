"""Idempotent Airflow metastore setup. Secrets become encrypted Connections."""
import os
from airflow.models import Connection
from airflow.utils.session import create_session
from airflow.www.app import create_app
from flask_appbuilder.security.manager import AUTH_DB

def env(name):
    return os.environ[name]
connections = [
    Connection(conn_id='rutanova_minio', conn_type='aws', login=env('MINIO_ACCESS_KEY'),
               password=env('MINIO_SECRET_KEY'), extra={'endpoint_url': 'http://minio:9000', 'bucket': 'rutanova-raw'}),
    Connection(conn_id='rutanova_api', conn_type='http', host='http://orders-api:8000'),
    Connection(conn_id='rutanova_snowflake', conn_type='snowflake', login=env('SNOWFLAKE_USER'),
               password=os.environ.get('SNOWFLAKE_PASSWORD') or None,
               schema='ANALYTICS', extra={'account': env('SNOWFLAKE_ACCOUNT'), 'database': env('SNOWFLAKE_DATABASE'),
                'warehouse': env('SNOWFLAKE_WAREHOUSE'), 'role': env('SNOWFLAKE_ROLE'),
                'auth': env('SNOWFLAKE_AUTH'), 'private_key_path': env('SNOWFLAKE_PRIVATE_KEY_PATH')}),
]
with create_session() as session:
    for conn in connections:
        old = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()
        if old:
            session.delete(old)
            session.flush()
        session.add(conn)
app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    user = sm.find_user(username=env('AIRFLOW_ADMIN_USER'))
    if not user:
        sm.add_user(username=env('AIRFLOW_ADMIN_USER'), first_name='Ruta', last_name='Nova',
                    email='admin@example.invalid', role=sm.find_role('Admin'), password=env('AIRFLOW_ADMIN_PASSWORD'))
print('Airflow user and Connections initialized. No credential values printed.')
