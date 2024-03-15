#!/bin/bash

# Start postgress
docker-entrypoint.sh postgres &

# Wait postgress
until pg_isready --host=127.0.0.1; do sleep 1 && echo "waiting for postgres"; done

# Start MaxKB
python /opt/maxkb/app/main.py start