#!/bin/bash

mkdir -p /opt/maxkb/data/postgresql
docker-entrypoint.sh postgres -c max_connections=${POSTGRES_MAX_CONNECTIONS}
