#!/bin/bash

mkdir -p /opt/maxkb/logs
mkdir -p /opt/maxkb/local
mkdir -p /opt/maxkb/python-packages

rm -f /opt/maxkb-app/tmp/*.pid
python /opt/maxkb-app/main.py start