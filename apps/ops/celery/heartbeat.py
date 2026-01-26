import os
from pathlib import Path

from celery.signals import heartbeat_sent, worker_ready, worker_shutdown

def _get_tmpdir() -> Path:
    tmpdir = os.environ.get('TMPDIR') or '/opt/maxkb-app/tmp'
    path = Path(tmpdir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@heartbeat_sent.connect
def heartbeat(sender, **kwargs):
    worker_name = sender.eventer.hostname.split('@')[0]
    heartbeat_path = _get_tmpdir() / f'worker_heartbeat_{worker_name}'
    heartbeat_path.touch()


@worker_ready.connect
def worker_ready(sender, **kwargs):
    worker_name = sender.hostname.split('@')[0]
    ready_path = _get_tmpdir() / f'worker_ready_{worker_name}'
    ready_path.touch()


@worker_shutdown.connect
def worker_shutdown(sender, **kwargs):
    worker_name = sender.hostname.split('@')[0]
    tmpdir = _get_tmpdir()
    for signal in ['ready', 'heartbeat']:
        path = tmpdir / f'worker_{signal}_{worker_name}'
        path.unlink(missing_ok=True)
