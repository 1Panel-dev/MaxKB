#!/bin/bash

if [ "$MAXKB_DB_HOST" = "127.0.0.1" ]; then
    echo "PostgreSQL starting..."
    /usr/bin/start-postgres.sh
    echo "PostgreSQL started."
fi


if [ "$MAXKB_REDIS_HOST" = "127.0.0.1" ]; then
    echo "Redis starting..."
    /usr/bin/start-redis.sh
    echo "Redis started."
fi

/usr/bin/start-maxkb.sh