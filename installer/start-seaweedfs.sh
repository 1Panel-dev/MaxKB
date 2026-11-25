#!/bin/bash

if [ ! -d "${SEAWEEDFS_VOLUMES:-/opt/maxkb/data/seaweedfs}" ]; then
    mkdir -p "${SEAWEEDFS_VOLUMES:-/opt/maxkb/data/seaweedfs}"
    chmod 700 "${SEAWEEDFS_VOLUMES:-/opt/maxkb/data/seaweedfs}"
fi

S3_ENDPOINT="${SEAWEEDFS_S3_ENDPOINT:-http://127.0.0.1:8333}"
S3_PORT="${S3_ENDPOINT##*:}"

AWS_ACCESS_KEY_ID="${SEAWEEDFS_ACCESS_KEY:-seaweedfsadmin}" \
AWS_SECRET_ACCESS_KEY="${SEAWEEDFS_SECRET_KEY:-seaweedfsadmin}" \
S3_BUCKET="${SEAWEEDFS_S3_BUCKET:-maxkb}" \
/usr/local/bin/weed mini \
  -dir="${SEAWEEDFS_VOLUMES:-/opt/maxkb/data/seaweedfs}" \
  -s3.port="$S3_PORT"
