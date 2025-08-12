#!/bin/bash

if [ ! -d /opt/maxkb/logs ]; then
    mkdir -p /opt/maxkb/logs
    chmod 700 /opt/maxkb/logs
fi
if [ ! -d /opt/maxkb/local ]; then
    mkdir -p /opt/maxkb/local
    chmod 700 /opt/maxkb/local
fi
mkdir -p /opt/maxkb/python-packages

rm -f /opt/maxkb-app/tmp/*.pid
python /opt/maxkb-app/main.py start