import os
import subprocess

from .celery_base import CeleryBaseService
from django.conf import settings

__all__ = ['CeleryDefaultService']


class CeleryDefaultService(CeleryBaseService):

    def __init__(self, **kwargs):
        kwargs['queue'] = 'celery'
        super().__init__(**kwargs)

    def open_subprocess(self):
        env = os.environ.copy()
        env['LC_ALL'] = 'C.UTF-8'
        env['PYTHONOPTIMIZE'] = '1'
        env['ANSIBLE_FORCE_COLOR'] = 'True'
        env['PYTHONPATH'] = settings.APPS_DIR
        env['SERVER_NAME'] = 'celery'
        if os.getuid() == 0:
            env.setdefault('C_FORCE_ROOT', '1')
        kwargs = {
            'cwd': self.cwd,
            'stderr': self.log_file,
            'stdout': self.log_file,
            'env': env
        }
        self._process = subprocess.Popen(self.cmd, **kwargs)
