import boto3
from botocore.client import Config
from maxkb.const import CONFIG


def is_rustfs_enabled() -> bool:
    return bool(CONFIG.get("RUSTFS_ADDRESS"))


def get_bucket() -> str:
    return CONFIG.get("RUSTFS_BUCKET") or "maxkb"


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=CONFIG.get("RUSTFS_ADDRESS"),
        aws_access_key_id=CONFIG.get("RUSTFS_ACCESS_KEY"),
        aws_secret_access_key=CONFIG.get("RUSTFS_SECRET_KEY"),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
