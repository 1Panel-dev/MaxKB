# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_code.py
    @date：2024/8/7 16:11
    @desc:
"""
import os
import subprocess
import sys
import uuid
from textwrap import dedent

from diskcache import Cache

python_directory = sys.executable


class FunctionExecutor:
    def __init__(self, result_path):
        self.result_path = result_path
        self._createdir()
        self.cache = Cache(self.result_path)

    def _createdir(self):
        old_mask = os.umask(0o077)
        try:
            os.makedirs(self.result_path, 0o700, exist_ok=True)
        finally:
            os.umask(old_mask)

    def exec_code(self, code_str, keywords):
        _id = str(uuid.uuid1())
        c = '"""' + dedent(code_str) + '"""'
        success = '{"code":200,"msg":"成功","data":exec_result}'
        err = '{"code":500,"msg":str(e),"data":None}'
        path = r'' + self.result_path + ''
        _exec_code = f"""
try:
    locals_v={'{}'}
    keywords={keywords}
    globals_v=globals()
    exec({c}, globals_v, locals_v)
    f_name, f = locals_v.popitem()
    for local in locals_v:
        globals_v[local] = locals_v[local]
    exec_result=f(**keywords)
    from diskcache import Cache
    cache = Cache({path!a})
    cache.set({_id!a},{success})
except Exception as e:
    from diskcache import Cache
    cache = Cache({path!a})
    cache.set({_id!a},{err})
"""
        subprocess_result = subprocess.run([python_directory, '-c', _exec_code], text=True, capture_output=True)
        if subprocess_result.returncode == 1:
            raise Exception(subprocess_result.stderr)
        result = self.cache.get(_id)
        self.cache.delete(_id)
        if result.get('code') == 200:
            return result.get('data')
        raise Exception(result.get('msg'))
