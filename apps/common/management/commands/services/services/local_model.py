# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： local_model.py
    @date：2024/8/21 13:28
    @desc:
"""
from .base import BaseService
from ..hands import *

__all__ = ['GunicornLocalModelService']


class GunicornLocalModelService(BaseService):

    def __init__(self, **kwargs):
        self.worker = kwargs['worker_gunicorn']
        super().__init__(**kwargs)

    @property
    def cmd(self):
        print("\n- Start Gunicorn Local Model WSGI HTTP Server")
        os.environ.setdefault('SERVER_NAME', 'local_model')
        log_format = '%(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s '
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        worker = CONFIG.get("LOCAL_MODEL_HOST_WORKER", 1)
        cmd = [
            'gunicorn', 'smartdoc.wsgi:application',
            '-b', bind,
            '-k', 'gthread',
            '--threads', '200',
            '-w', str(worker),
            '--max-requests', '10240',
            '--max-requests-jitter', '2048',
            '--access-logformat', log_format,
            '--access-logfile', '-'
        ]
        if DEBUG:
            cmd.append('--reload')
        return cmd

    @property
    def cwd(self):
        return APPS_DIR
