# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： web.py
    @date：2025/11/5 15:14
    @desc:
"""
import builtins
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
            print(f"Disable package is being imported: 【{name}】", file=sys.stderr)
            pass
        else:
            return self.original_import(name, *args, **kwargs)


# 安装导入拦截器
builtins.__import__ = TorchBlocker()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
os.environ['TIKTOKEN_CACHE_DIR'] = '/opt/maxkb-app/model/tokenizer/openai-tiktoken-cl100k-base'
application = get_wsgi_application()


def post_handler():
    from common.database_model_manage.database_model_manage import DatabaseModelManage
    from common import event

    event.run()
    DatabaseModelManage.init()


# 启动后处理函数
post_handler()
