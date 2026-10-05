FROM apache/airflow:2.10.5-python3.11
USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir "apache-airflow==2.10.5" -r /tmp/requirements.txt     && python -m venv /opt/airflow/dbt-venv     && /opt/airflow/dbt-venv/bin/pip install --no-cache-dir dbt-core==1.9.4 dbt-snowflake==1.9.2
COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root src /opt/airflow/src
COPY --chown=airflow:root scripts /opt/airflow/scripts
COPY --chown=airflow:root dbt /opt/airflow/dbt
COPY --chown=airflow:root tests /opt/airflow/tests
COPY --chown=airflow:root api /opt/airflow/api
COPY --chown=airflow:root inbox /opt/airflow/inbox
RUN mkdir -p /opt/airflow/dbt/target /opt/airflow/dbt/logs
ENV PYTHONPATH=/opt/airflow
