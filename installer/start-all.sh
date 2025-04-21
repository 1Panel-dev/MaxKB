#!/bin/bash

set -e

if [ "$MAXKB_DB_HOST" = "127.0.0.1" ]; then
  echo "PostgreSQL starting..."
  /usr/bin/start-postgres.sh &
  sleep 10
  wait-for-it 127.0.0.1:5432 --timeout=120 --strict -- echo "PostgreSQL started."
fi

if [ "$MAXKB_REDIS_HOST" = "127.0.0.1" ]; then
  echo "Redis starting..."
  /usr/bin/start-redis.sh &
  sleep 5
  wait-for-it 127.0.0.1:6379 --timeout=60 --strict -- echo "Redis started."
fi

/usr/bin/start-maxkb.sh