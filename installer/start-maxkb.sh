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

INIT_SHELL_DIR="/opt/maxkb/local/init-shells"
if [ -d "$INIT_SHELL_DIR" ]; then
    find "$INIT_SHELL_DIR" -maxdepth 1 -type f -name "*.sh" | sort | while IFS= read -r f; do
        if bash "$f"; then
            echo "[OK] init-shell >>> $f"
        else
            echo "[ERROR] init-shell >>> $f failed with exit code $?" >&2
        fi
    done
fi

python /opt/maxkb-app/main.py start