#!/bin/bash

set -e

if [ "$MAXKB_DB_HOST" = "127.0.0.1" ]; then
    /usr/bin/start-postgres.sh
fi

if [ "$MAXKB_REDIS_HOST" = "127.0.0.1" ]; then
    /usr/bin/start-redis.sh
fi

/usr/bin/start-maxkb.sh