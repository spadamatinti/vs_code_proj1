#!/usr/bin/env python3
import os
import argparse
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


class ProgressPercentage:
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._tqdm = tqdm(total=self._size, unit='B', unit_scale=True, desc=os.path.basename(filename)) if tqdm else None

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        if self._tqdm:
            self._tqdm.update(bytes_amount)
        else:
            percent = (self._seen_so_far / self._size) * 100
            print(f"\r{self._seen_so_far} / {self._size}  ({percent:.2f}%)", end='')

    def close(self):
        if self._tqdm:
            self._tqdm.close()
        else:
            print()


def upload_file(local_path: str, bucket: str, key: str, profile: str = None, region: str = None, extra_args: dict = None):
    """Upload a local file to S3.

    Args:
        local_path: Local file path
        bucket: S3 bucket name
        key: S3 object key (path in bucket)
        profile: Optional AWS CLI profile name
        region: Optional AWS region
        extra_args: Optional dict of ExtraArgs passed to upload_file (e.g., {'ACL': 'public-read'})
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")

    session_kwargs = {}
    if profile:
        session_kwargs['profile_name'] = profile
    if region:
        session_kwargs['region_name'] = region

    session = boto3.Session(**session_kwargs) if session_kwargs else boto3.Session()
    s3 = session.client('s3')

    config = TransferConfig(multipart_threshold=8 * 1024 * 1024, multipart_chunksize=8 * 1024 * 1024, max_concurrency=4)

    progress = ProgressPercentage(local_path)
    try:
        s3.upload_file(local_path, bucket, key, ExtraArgs=extra_args or {}, Callback=progress, Config=config)
    except ClientError:
        progress.close()
        raise
    progress.close()


def parse_s3_uri(s3_uri: str):
    if not s3_uri.startswith('s3://'):
        raise ValueError('s3_uri must start with s3://')
    parts = s3_uri[5:].split('/', 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ''
    return bucket, key


def main():
    parser = argparse.ArgumentParser(description='Upload a local file to S3')
    parser.add_argument('local_path', help='Local file to upload')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--s3-uri', help='Destination S3 URI (s3://bucket/key)')
    group.add_argument('--bucket-key', nargs=2, metavar=('BUCKET', 'KEY'), help='Destination bucket and key')
    parser.add_argument('--profile', help='AWS CLI profile name')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--acl', help='Canned ACL to set on the object (e.g., public-read)')
    parser.add_argument('--storage-class', help='Storage class (e.g., STANDARD, ONEZONE_IA)')

    args = parser.parse_args()

    if args.s3_uri:
        bucket, key = parse_s3_uri(args.s3_uri)
    else:
        bucket, key = args.bucket_key

    extra_args = {}
    if args.acl:
        extra_args['ACL'] = args.acl
    if args.storage_class:
        extra_args['StorageClass'] = args.storage_class

    try:
        upload_file(args.local_path, bucket, key, profile=args.profile, region=args.region, extra_args=extra_args)
        print(f"Uploaded {args.local_path} to s3://{bucket}/{key}")
    except Exception as e:
        print(f"Upload failed: {e}")
        raise


if __name__ == '__main__':
    main()
