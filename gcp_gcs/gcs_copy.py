#!/usr/bin/env python3
import os
import argparse

try:
    from tqdm import tqdm
except Exception:
    tqdm = None

from google.cloud import storage


def parse_gcs_uri(gcs_uri: str):
    if not gcs_uri.startswith('gs://'):
        raise ValueError('gcs_uri must start with gs://')
    parts = gcs_uri[5:].split('/', 1)
    bucket = parts[0]
    object_name = parts[1] if len(parts) > 1 else ''
    return bucket, object_name


def download_file(local_path: str, bucket: str, object_name: str, project: str = None, credentials_path: str = None):
    """Download a blob from Google Cloud Storage to a local file.

    Args:
        local_path: Destination local file path
        bucket: GCS bucket name
        object_name: GCS object name (path in bucket)
        project: Optional GCP project for the `storage.Client`
        credentials_path: Optional path to service account JSON file. If provided,
            the environment variable `GOOGLE_APPLICATION_CREDENTIALS` will be set
            for the call.
    """
    if credentials_path:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    # Ensure local directory exists
    dest_dir = os.path.dirname(os.path.abspath(local_path))
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    # Create client
    client_kwargs = {}
    if project:
        client_kwargs['project'] = project
    client = storage.Client(**client_kwargs) if client_kwargs else storage.Client()

    bucket_obj = client.bucket(bucket)
    blob = bucket_obj.blob(object_name)

    if not blob.exists():
        raise FileNotFoundError(f'GCS object not found: gs://{bucket}/{object_name}')

    blob.download_to_filename(local_path)


def main():
    parser = argparse.ArgumentParser(description='Download a file from GCS to local path')
    parser.add_argument('local_path', help='Local destination path')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--gcs-uri', help='Source GCS URI (gs://bucket/object)')
    group.add_argument('--bucket-object', nargs=2, metavar=('BUCKET', 'OBJECT'), help='Source bucket and object')
    parser.add_argument('--project', help='GCP project')
    parser.add_argument('--credentials', help='Path to service account JSON file')

    args = parser.parse_args()

    if args.gcs_uri:
        bucket, object_name = parse_gcs_uri(args.gcs_uri)
    else:
        bucket, object_name = args.bucket_object

    download_file(args.local_path, bucket, object_name, project=args.project, credentials_path=args.credentials)


if __name__ == '__main__':
    main()
