#!/bin/bash

mkdir -p /opt/maxkb/data/redis

if [ ! -f /opt/maxkb/conf/redis.conf ]; then
  mkdir -p /opt/maxkb/conf
  touch /opt/maxkb/conf/redis.conf
  printf "bind 0.0.0.0\nport 6379\ndatabases 16\nmaxmemory 1G\nmaxmemory-policy allkeys-lru\ndir /opt/maxkb/data/redis\nrequirepass "${REDIS_PASSWORD}"\n" > /opt/maxkb/conf/redis.conf
fi
echo "Redis starting..."
redis-server /opt/maxkb/conf/redis.conf &
sleep 5
/usr/bin/wait-for-it.sh 127.0.0.1:6379 --timeout=60 --strict -- echo "Redis started."