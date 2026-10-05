"""Additional integration tests run only in the Airflow image."""
from pathlib import Path
import pytest
pytest.importorskip('airflow')
from airflow.models import DagBag

def test_dag_contract():
    bag=DagBag(dag_folder=str(Path(__file__).resolve().parents[1]/'dags'),include_examples=False)
    assert bag.import_errors == {}
    dag=bag.dags.get('rutanova_profitability')
    assert dag is not None and dag.catchup is False and dag.max_active_runs == 1
    assert dag.schedule_interval == '0 7 * * *'
    assert len(dag.task_dict) == 6
    assert dag.get_task('ingestion.wait_delivery_csv').mode == 'reschedule'
    assert dag.get_task('transformation.dbt_build').upstream_task_ids == {'warehouse.load_atomic_snapshot'}
