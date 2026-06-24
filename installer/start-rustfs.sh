#!/bin/bash

set -e

mkdir -p "${RUSTFS_VOLUMES:-/opt/maxkb/data/rustfs}"
mkdir -p "${RUSTFS_OBS_LOG_DIRECTORY:-/opt/maxkb/log/rustfs}"

/usr/local/bin/rustfs "${RUSTFS_VOLUMES:-/opt/maxkb/data/rustfs}" &
RUSTFS_PID=$!

wait-for-it 127.0.0.1:9000 --timeout=60 --strict && python3 << 'EOF'
import boto3, os, sys
from botocore.client import Config

addr = os.environ.get("RUSTFS_ADDRESS", "")
if not addr:
    sys.exit(0)

if not addr.startswith(("http://", "https://")):
    addr = f"http://{addr}"

s3 = boto3.client(
    "s3",
    endpoint_url=addr,
    aws_access_key_id=os.environ.get("RUSTFS_ACCESS_KEY", ""),
    aws_secret_access_key=os.environ.get("RUSTFS_SECRET_KEY", ""),
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

bucket = os.environ.get("RUSTFS_BUCKET", "maxkb")
try:
    s3.head_bucket(Bucket=bucket)
    print(f"RustFS bucket '{bucket}' already exists")
except Exception:
    s3.create_bucket(Bucket=bucket)
    print(f"RustFS bucket '{bucket}' created")
EOF

trap "kill $RUSTFS_PID 2>/dev/null" TERM INT
wait $RUSTFS_PID
