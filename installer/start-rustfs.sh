#!/bin/bash

set -e

mkdir -p "${RUSTFS_VOLUMES:-/opt/maxkb/data/rustfs}"
mkdir -p "${RUSTFS_OBS_LOG_DIRECTORY:-/opt/maxkb/log/rustfs}"

exec /usr/local/bin/rustfs "${RUSTFS_VOLUMES:-/opt/maxkb/data/rustfs}"
