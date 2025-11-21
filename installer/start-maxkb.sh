#!/bin/bash

if [ ! -d /opt/maxkb/logs ]; then
    mkdir -p /opt/maxkb/logs
fi
chmod -R 700 /opt/maxkb/logs
if [ ! -d /opt/maxkb/local ]; then
    mkdir -p /opt/maxkb/local
    chmod 700 /opt/maxkb/local
fi
mkdir -p /opt/maxkb/python-packages

rm -f /opt/maxkb-app/tmp/*
python /opt/maxkb-app/main.py start