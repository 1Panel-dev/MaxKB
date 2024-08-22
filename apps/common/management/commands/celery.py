# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： celery.py
    @date：2024/8/19 11:57
    @desc:
"""
import os
import subprocess

from django.core.management.base import BaseCommand

from smartdoc.const import BASE_DIR


class Command(BaseCommand):
    help = 'celery'

    def add_arguments(self, parser):
        parser.add_argument(
            'service', nargs='+', type=str, choices=("celery", "model"), help='Service',
        )

    def handle(self, *args, **options):
        service = options.get('service')
        os.environ.setdefault('CELERY_NAME', ','.join(service))
        server_hostname = os.environ.get("SERVER_HOSTNAME")
        if hasattr(os, 'getuid') and os.getuid() == 0:
            os.environ.setdefault('C_FORCE_ROOT', '1')
        if not server_hostname:
            server_hostname = '%h'
        cmd = [
            'celery',
            '-A', 'ops',
            'worker',
            '-P', 'threads',
            '-l', 'info',
            '-c', '10',
            '-Q', ','.join(service),
            '--heartbeat-interval', '10',
            '-n', f'{",".join(service)}@{server_hostname}',
            '--without-mingle',
        ]
        kwargs = {'cwd': BASE_DIR}
        subprocess.run(cmd, **kwargs)
