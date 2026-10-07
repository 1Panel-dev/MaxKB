# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： web.py
    @date：2025/11/5 15:14
    @desc:
"""
import builtins
import csv
import os
import sys

from django.core.wsgi import get_wsgi_application


class TorchBlocker:
    def __init__(self):
        self.original_import = builtins.__import__

    def __call__(self, name, *args, **kwargs):
        if len([True for i in
                ['torch']
                if
                i in name.lower()]) > 0:
            import types
            return types.ModuleType(name)
        else:
            return self.original_import(name, *args, **kwargs)


# 安装导入拦截器
builtins.__import__ = TorchBlocker()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
os.environ['TIKTOKEN_CACHE_DIR'] = '/opt/maxkb-app/model/tokenizer/openai-tiktoken-cl100k-base'
# csv.field_size_limit 在 Windows 上为 32 位 C long，直接传 sys.maxsize 会 OverflowError，需逐步回退
_csv_field_size_limit = sys.maxsize
while True:
    try:
        csv.field_size_limit(_csv_field_size_limit)
        break
    except OverflowError:
        _csv_field_size_limit = int(_csv_field_size_limit / 10)
application = get_wsgi_application()


def post_handler():
    from common.database_model_manage.database_model_manage import DatabaseModelManage
    from common import event
    from common.init import init_template
    event.run()
    DatabaseModelManage.init()
    init_template.run()


# 启动后处理函数
post_handler()
