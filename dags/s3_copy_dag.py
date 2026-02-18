"""Airflow DAG to run the s3_copy `upload_file` function.

This DAG reads parameters from Airflow Variables (prefix `s3_copy_`).
Set at least `s3_copy_local_path` and either `s3_copy_s3_uri` or `s3_copy_bucket` and `s3_copy_key`.
"""
from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Ensure project root is on path so we can import s3_copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from s3_copy import upload_file, parse_s3_uri

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='s3_copy_upload',
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['s3', 'upload'],
) as dag:

    def _run_upload(**context):
        local_path = Variable.get('s3_copy_local_path', default_var=None)
        s3_uri = Variable.get('s3_copy_s3_uri', default_var=None)
        bucket = Variable.get('s3_copy_bucket', default_var=None)
        key = Variable.get('s3_copy_key', default_var=None)
        profile = Variable.get('s3_copy_profile', default_var=None)
        region = Variable.get('s3_copy_region', default_var=None)
        acl = Variable.get('s3_copy_acl', default_var=None)
        storage_class = Variable.get('s3_copy_storage_class', default_var=None)

        if not local_path:
            raise ValueError('Airflow Variable `s3_copy_local_path` is required')

        extra_args = {}
        if acl:
            extra_args['ACL'] = acl
        if storage_class:
            extra_args['StorageClass'] = storage_class

        if s3_uri:
            bucket, key = parse_s3_uri(s3_uri)

        if not bucket or not key:
            raise ValueError('Either `s3_copy_s3_uri` or both `s3_copy_bucket` and `s3_copy_key` must be set')

        upload_file(local_path, bucket, key, profile=profile or None, region=region or None, extra_args=extra_args or None)

    upload_task = PythonOperator(
        task_id='upload_file_to_s3',
        python_callable=_run_upload,
        provide_context=True,
    )

    upload_task
