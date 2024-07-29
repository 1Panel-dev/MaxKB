# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： gunicorn.py
    @date：2024/7/19 17:43
    @desc:
"""
import subprocess

from django.core.management.base import BaseCommand

from smartdoc.const import BASE_DIR


class Command(BaseCommand):
    help = 'My custom command'

    # 参数设定
    def add_arguments(self, parser):
        parser.add_argument('-b', nargs='+', type=str, help="端口:0.0.0.0:8080")  # 0.0.0.0:8080
        parser.add_argument('-k', nargs='?', type=str,
                            help="workers处理器:gevent")  # uvicorn.workers.UvicornWorker
        parser.add_argument('-w', type=str, help='worker 数量')  # 进程数量
        parser.add_argument('--threads', type=str, help='线程数量')  # 线程数量
        parser.add_argument('--worker-connections', type=str, help="每个线程的协程数量")  # 10240
        parser.add_argument('--max-requests', type=str, help="最大请求")  # 10240
        parser.add_argument('--max-requests-jitter', type=str)
        parser.add_argument('--access-logformat', type=str)  # %(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s

    def handle(self, *args, **options):
        log_format = '%(h)s %(t)s %(L)ss "%(r)s" %(s)s %(b)s '
        cmd = [
            'gunicorn', 'smartdoc.wsgi:application',
            '-b', options.get('b') if options.get('b') is not None else '0.0.0.0:8080',
            '-k', options.get('k') if options.get('k') is not None else 'gthread',
            '--threads', options.get('threads') if options.get('threads') is not None else '200',
            '-w', options.get('w') if options.get('w') is not None else '1',
            '--max-requests', options.get('max_requests') if options.get('max_requests') is not None else '10240',
            '--max-requests-jitter',
            options.get('max_requests_jitter') if options.get('max_requests_jitter') is not None else '2048',
            '--access-logformat',
            options.get('access_logformat') if options.get('access_logformat') is not None else log_format,
            '--access-logfile', '-'
        ]
        kwargs = {'cwd': BASE_DIR}
        subprocess.run(cmd, **kwargs)
