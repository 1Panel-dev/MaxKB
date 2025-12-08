import argparse
import logging
import os
import sys
import time

import django
from django.core import management

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'apps')

os.chdir(BASE_DIR)
sys.path.insert(0, APP_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maxkb.settings")


def collect_static():
    """
     收集静态文件到指定目录
     本项目主要是将前端vue/dist的前端项目放到静态目录下面
    :return:
    """
    logging.info("Collect static files")
    try:
        management.call_command('collectstatic', '--no-input', '-c', verbosity=0, interactive=False)
        logging.info("Collect static files done")
    except:
        pass


def perform_db_migrate():
    """
    初始化数据库表
    """
    logging.info("Check database structure change ...")
    logging.info("Migrate model change to database ...")
    try:
        management.call_command('migrate')
    except Exception as e:
        logging.error('Perform migrate failed, exit', exc_info=True)
        sys.exit(11)


def start_services():
    services = args.services if isinstance(args.services, list) else [args.services]
    start_args = []
    if args.daemon:
        start_args.append('--daemon')
    if args.force:
        start_args.append('--force')
    if args.worker:
        start_args.extend(['--worker', str(args.worker)])
    else:
        worker = os.environ.get('MAXKB_CORE_WORKER')
        if isinstance(worker, str) and worker.isdigit():
            start_args.extend(['--worker', worker])

    try:
        management.call_command(action, *services, *start_args)
    except KeyboardInterrupt:
        logging.info('Cancel ...')
        time.sleep(2)
    except Exception as exc:
        logging.error("Start service error {}: {}".format(services, exc))
        time.sleep(2)


def dev():
    services = args.services if isinstance(args.services, list) else args.services
    if services.__contains__('web'):
        management.call_command('runserver', "0.0.0.0:8080")
    elif services.__contains__('celery'):
        management.call_command('celery', 'celery')
    elif services.__contains__('local_model'):
        from maxkb.const import CONFIG
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        management.call_command('runserver', bind)


if __name__ == '__main__':
    os.environ['HF_HOME'] = '/opt/maxkb-app/model/base'
    parser = argparse.ArgumentParser(
        description="""
           qabot service control tools;

           Example: \r\n

           %(prog)s start all -d;
           """
    )
    parser.add_argument(
        'action', type=str,
        choices=("start", "dev", "upgrade_db", "collect_static"),
        help="Action to run"
    )
    args, e = parser.parse_known_args()
    parser.add_argument(
        "services", type=str, default='all' if args.action == 'start' else 'web', nargs="*",
        choices=("all", "web", "task") if args.action == 'start' else ("web", "celery", 'local_model'),
        help="The service to start",
    )

    parser.add_argument('-d', '--daemon', nargs="?", const=True)
    parser.add_argument('-w', '--worker', type=int, nargs="?")
    parser.add_argument('-f', '--force', nargs="?", const=True)
    args = parser.parse_args()
    action = args.action
    services = args.services if isinstance(args.services, list) else args.services
    if services.__contains__('web'):
        os.environ.setdefault('SERVER_NAME', 'web')
    elif services.__contains__('local_model'):
        os.environ.setdefault('SERVER_NAME', 'local_model')
    django.setup()
    if action == "upgrade_db":
        perform_db_migrate()
    elif action == "collect_static":
        collect_static()
    elif action == 'dev':
        collect_static()
        perform_db_migrate()
        dev()
    else:
        collect_static()
        perform_db_migrate()
        start_services()
