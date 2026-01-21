import os
from pathlib import Path

from celery.signals import heartbeat_sent, worker_ready, worker_shutdown

# 获取临时目录路径，兼容Windows和Linux
def get_tmp_dir():
    """获取临时目录，优先使用环境变量TMPDIR，否则使用项目目录下的tmp"""
    tmp_dir = os.environ.get('TMPDIR', None)
    if tmp_dir and os.path.exists(os.path.dirname(tmp_dir)):
        # 如果TMPDIR存在且父目录存在，使用它
        os.makedirs(tmp_dir, mode=0o700, exist_ok=True)
        return tmp_dir
    else:
        # 否则使用项目目录下的tmp
        from maxkb.const import PROJECT_DIR
        tmp_dir = os.path.join(PROJECT_DIR, 'tmp')
        os.makedirs(tmp_dir, mode=0o700, exist_ok=True)
        return tmp_dir


@heartbeat_sent.connect
def heartbeat(sender, **kwargs):
    try:
        worker_name = sender.eventer.hostname.split('@')[0]
        tmp_dir = get_tmp_dir()
        heartbeat_path = Path(tmp_dir) / 'worker_heartbeat_{}'.format(worker_name)
        heartbeat_path.touch()
    except Exception:
        # 忽略心跳错误，避免影响Celery运行
        pass


@worker_ready.connect
def worker_ready(sender, **kwargs):
    try:
        worker_name = sender.hostname.split('@')[0]
        tmp_dir = get_tmp_dir()
        ready_path = Path(tmp_dir) / 'worker_ready_{}'.format(worker_name)
        ready_path.touch()
    except Exception:
        # 忽略就绪信号错误
        pass


@worker_shutdown.connect
def worker_shutdown(sender, **kwargs):
    try:
        worker_name = sender.hostname.split('@')[0]
        tmp_dir = get_tmp_dir()
        for signal in ['ready', 'heartbeat']:
            path = Path(tmp_dir) / 'worker_{}_{}'.format(signal, worker_name)
            path.unlink(missing_ok=True)
    except Exception:
        # 忽略关闭信号错误
        pass
