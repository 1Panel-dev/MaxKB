import subprocess

from .base import BaseService
from ..hands import *

__all__ = ['GunicornService']


class GunicornService(BaseService):

    def __init__(self, **kwargs):
        self.worker = kwargs['worker_gunicorn']
        super().__init__(**kwargs)

    @property
    def cmd(self):
        print("\n- Start Gunicorn WSGI HTTP Server")

        log_format = '%(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s '
        bind = f'{HTTP_HOST}:{HTTP_PORT}'
        max_requests = 10240 if int(self.worker) > 1 else 0
        cmd = [
            'gunicorn', 'maxkb.wsgi:application',
            '-b', bind,
            '-k', 'gthread',
            '--threads', '200',
            '-w', str(self.worker),
            '--max-requests', str(max_requests),
            '--max-requests-jitter', '2048',
            '--timeout', '0',
            '--graceful-timeout', '0',
            '--access-logformat', log_format,
            '--access-logfile', '/dev/null',
            '--error-logfile', '-'
        ]
        if DEBUG:
            cmd.append('--reload')
        return cmd

    @property
    def cwd(self):
        return APPS_DIR

    def open_subprocess(self):
        # 复制当前环境变量，并设置 ENABLE_SCHEDULER=1
        env = os.environ.copy()
        env['SERVER_NAME'] = 'web'
        kwargs = {
            'cwd': self.cwd,
            'stderr': self.log_file,
            'stdout': self.log_file,
            'env': env
        }
        self._process = subprocess.Popen(self.cmd, **kwargs)
