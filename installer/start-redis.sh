#!/bin/bash

mkdir -p /opt/maxkb/data/redis

if [ ! -f /opt/maxkb/conf/redis.conf ]; then
  mkdir -p /opt/maxkb/conf
  touch /opt/maxkb/conf/redis.conf
  printf "bind 0.0.0.0\nport 6379\ndatabases 16\nmaxmemory 1G\nmaxmemory-policy allkeys-lru\ndir /opt/maxkb/data/redis\nrequirepass "${REDIS_PASSWORD}"\n" > /opt/maxkb/conf/redis.conf
fi

redis-server /opt/maxkb/conf/redis.conf