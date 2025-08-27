import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from .config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )


def upload_file_to_s3(local_path: str, s3_key: Optional[str] = None, bucket: Optional[str] = None) -> str:
    s3_key = s3_key or settings.model_s3_key
    bucket = bucket or settings.s3_bucket
    client = get_s3_client()
    client.upload_file(local_path, bucket, s3_key)
    return f"s3://{bucket}/{s3_key}"


def download_file_from_s3(s3_key: Optional[str] = None, local_path: Optional[str] = None, bucket: Optional[str] = None) -> str:
    s3_key = s3_key or settings.model_s3_key
    local_path = local_path or settings.model_local_path
    bucket = bucket or settings.s3_bucket

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    client = get_s3_client()
    client.download_file(bucket, s3_key, local_path)
    return local_path
