"""Airflow DAG to run the gcp_gcs `download_file` function.

This DAG reads parameters from Airflow Variables (prefix `gcs_copy_`).
Set at least `gcs_copy_local_path` and either `gcs_copy_gcs_uri` or `gcs_copy_bucket` and `gcs_copy_object`.
"""
from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Ensure project root is on path so we can import gcp_gcs
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gcp_gcs.gcs_copy import download_file, parse_gcs_uri

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='gcs_copy_download',
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['gcs', 'download'],
) as dag:

    def _run_download(**context):
        local_path = Variable.get('gcs_copy_local_path', default_var=None)
        gcs_uri = Variable.get('gcs_copy_gcs_uri', default_var=None)
        bucket = Variable.get('gcs_copy_bucket', default_var=None)
        object_name = Variable.get('gcs_copy_object', default_var=None)
        project = Variable.get('gcs_copy_project', default_var=None)
        credentials = Variable.get('gcs_copy_credentials', default_var=None)

        if not local_path:
            raise ValueError('Airflow Variable `gcs_copy_local_path` is required')

        if gcs_uri:
            bucket, object_name = parse_gcs_uri(gcs_uri)

        if not bucket or not object_name:
            raise ValueError('Either `gcs_copy_gcs_uri` or both `gcs_copy_bucket` and `gcs_copy_object` must be set')

        download_file(local_path, bucket, object_name, project=project or None, credentials_path=credentials or None)

    download_task = PythonOperator(
        task_id='download_file_from_gcs',
        python_callable=_run_download,
        provide_context=True,
    )

    download_task
