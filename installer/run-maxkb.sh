#!/bin/bash

# Start postgresql
docker-entrypoint.sh postgres &
sleep 10
# Wait postgresql
until pg_isready --host=127.0.0.1; do sleep 1 && echo "waiting for postgres"; done

# Start MaxKB
python /opt/maxkb/app/main.py start