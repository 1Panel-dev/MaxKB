import boto3
from botocore.client import Config
from maxkb.const import CONFIG


def is_seaweedfs_enabled() -> bool:
    return bool(CONFIG.get("S3_ENDPOINT"))


def get_bucket() -> str:
    return CONFIG.get("S3_BUCKET") or "maxkb"


def get_s3_client():
    addr = CONFIG.get("S3_ENDPOINT") or ""
    if addr and not addr.startswith(("http://", "https://")):
        addr = f"http://{addr}"
    return boto3.client(
        "s3",
        endpoint_url=addr,
        aws_access_key_id=CONFIG.get("S3_ACCESS_KEY"),
        aws_secret_access_key=CONFIG.get("S3_SECRET_KEY"),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
