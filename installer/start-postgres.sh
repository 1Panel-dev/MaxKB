#!/bin/bash

mkdir -p /opt/maxkb/data/postgresql

docker-entrypoint.sh postgres -c max_connections=${POSTGRES_MAX_CONNECTIONS} &
sleep 10
/usr/bin/wait-for-it.sh 127.0.0.1:5432 --timeout=120 --strict