import os
import tempfile
import boto3
from moto import mock_s3
import pytest

from s3_copy import upload_file


@mock_s3
def test_upload_file_to_s3_creates_object():
    bucket = 'my-test-bucket'
    key = 'test/object.txt'

    # create a temp file
    fd, path = tempfile.mkstemp()
    os.close(fd)
    with open(path, 'w') as f:
        f.write('hello world')

    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket=bucket)

    try:
        upload_file(path, bucket, key)

        # verify object exists and contents match
        resp = s3.get_object(Bucket=bucket, Key=key)
        body = resp['Body'].read().decode()
        assert body == 'hello world'
    finally:
        os.remove(path)
