#!/bin/bash

set -e

if [ -f "/var/lib/postgresql/data/PG_VERSION" ]; then
  # 如果是v1版本一键安装的的目录则退出
  echo "The existing data is from v1 and is not compatible with v2, installing v2 over v1 is not supported."
  echo "The process will now exit."
  exit 1
fi

if [ "$MAXKB_DB_HOST" = "127.0.0.1" ]; then
  echo "PostgreSQL starting..."
  /usr/bin/start-postgres.sh &
  postgres_pid=$!
  sleep 10
  wait-for-it 127.0.0.1:5432 --timeout=120 --strict -- echo "PostgreSQL started."
fi

if [ "$MAXKB_REDIS_HOST" = "127.0.0.1" ]; then
  echo "Redis starting..."
  /usr/bin/start-redis.sh &
  redis_pid=$!
  sleep 5
  wait-for-it 127.0.0.1:6379 --timeout=60 --strict -- echo "Redis started."
fi

/usr/bin/start-maxkb.sh &
maxkb_pid=$!

wait -n
kill $postgres_pid $redis_pid $maxkb_pid 2>/dev/null
wait