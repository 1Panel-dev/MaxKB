#!/bin/bash

mkdir -p /opt/maxkb/data/postgresql
echo "PostgreSQL starting..."
docker-entrypoint.sh postgres -c max_connections=${POSTGRES_MAX_CONNECTIONS} &
sleep 10
wait-for-it 127.0.0.1:5432 --timeout=120 --strict -- echo "PostgreSQL started."