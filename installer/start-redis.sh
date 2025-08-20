#!/bin/bash

if [ ! -d /opt/maxkb/data/redis ]; then
    mkdir -p /opt/maxkb/data/redis
    chmod 700 /opt/maxkb/data/redis
fi
if [ ! -d /opt/maxkb/logs ]; then
    mkdir -p /opt/maxkb/logs
    chmod 700 /opt/maxkb/logs
fi
if [ ! -f /opt/maxkb/conf/redis.conf ]; then
  mkdir -p /opt/maxkb/conf
  touch /opt/maxkb/conf/redis.conf
  chmod 700 /opt/maxkb/conf/redis.conf
  cat <<EOF > /opt/maxkb/conf/redis.conf
bind 0.0.0.0
port 6379
databases 16
maxmemory 1G
aof-use-rdb-preamble yes
save 30 1
save 10 10
save 5 20
dbfilename dump.rdb
rdbcompression yes
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
maxmemory-policy allkeys-lru
loglevel warning
logfile /opt/maxkb/logs/redis.log
dir /opt/maxkb/data/redis
requirepass ${REDIS_PASSWORD}
EOF
fi

redis-server /opt/maxkb/conf/redis.conf