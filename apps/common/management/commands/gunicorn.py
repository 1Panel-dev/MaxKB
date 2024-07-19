# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： gunicorn.py
    @date：2024/7/19 17:43
    @desc:
"""
import os
import subprocess

from django.core.management.base import BaseCommand

from smartdoc.const import BASE_DIR


class Command(BaseCommand):
    help = 'My custom command'

    # 参数设定
    def add_arguments(self, parser):
        parser.add_argument('-b', nargs='+', type=str, help="端口:0.0.0.0:8080")  # 0.0.0.0:8080
        parser.add_argument('-k', nargs='?', type=str,
                            help="workers处理器:uvicorn.workers.UvicornWorker")  # uvicorn.workers.UvicornWorker
        parser.add_argument('-w', action='append', type=str, help='worker 数量')  # worker 数量
        parser.add_argument('--max-requests', action='append', type=str, help="最大请求")  # 10240
        parser.add_argument('--max-requests-jitter', action='append', type=str)
        parser.add_argument('--access-logformat', action='append', type=str)  # %(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s

    def handle(self, *args, **options):
        log_format = '%(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s '
        cmd = [
            'gunicorn', 'smartdoc.asgi:application',
            '-b', options.get('b', '0.0.0.0:8080'),
            '-k', options.get('k', 'uvicorn.workers.UvicornWorker'),
            '-w', options.get('w', '5'),
            '--max-requests', options.get('max_requests', '10240'),
            '--max-requests-jitter', options.get('max_requests_jitter', '2048'),
            '--access-logformat', options.get('access_logformat', log_format),
            '--access-logfile', '-'
        ]
        APPS_DIR = os.path.join(BASE_DIR, 'apps')
        kwargs = {'cwd': APPS_DIR}
        subprocess.run(cmd, **kwargs)
