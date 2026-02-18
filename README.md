# S3 Copy Example

This repository contains a small Python CLI (`s3_copy.py`) that uploads a local file to Amazon S3 using `boto3`.

Requirements

- Python 3.8+
- AWS credentials configured via environment variables or `~/.aws/credentials` (or pass `--profile`)

Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quick usage

```bash
# Upload using an S3 URI
python s3_copy.py /path/to/local/file --s3-uri s3://my-bucket/path/in/bucket.dat

# Upload by specifying bucket and key
python s3_copy.py /path/to/local/file --bucket-key my-bucket path/in/bucket.dat

# With ACL and storage class
python s3_copy.py /path/to/local/file --s3-uri s3://my-bucket/obj --acl public-read --storage-class ONEZONE_IA

# Use a named AWS profile
python s3_copy.py /path/to/local/file --s3-uri s3://my-bucket/obj --profile myprofile
```

Testing (uses `moto` to mock S3)

```bash
pytest -q
```

Notes

- `boto3` will read credentials from environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) or the AWS CLI config.
- The script uses `boto3.s3.transfer.TransferConfig` to handle multipart uploads for large files.
- If you want a progress bar, `tqdm` is used when installed.
