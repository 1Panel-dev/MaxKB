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

from smartdoc.const import BASE_DIR
from smartdoc.const import PROJECT_DIR

python_directory = sys.executable


class FunctionExecutor:
    def __init__(self, sandbox=False):
        self.sandbox = sandbox
        if sandbox:
            self.sandbox_path = '/opt/maxkb/app/sandbox'
            self.user = 'sandbox'
        else:
            self.sandbox_path = os.path.join(PROJECT_DIR, 'data', 'sandbox')
            self.user = None
        self._createdir()
        if self.sandbox:
            os.system(f"chown -R {self.user}:{self.user} {self.sandbox_path}")

    def _createdir(self):
        old_mask = os.umask(0o077)
        try:
            os.makedirs(self.sandbox_path, 0o700, exist_ok=True)
        finally:
            os.umask(old_mask)

    def exec_code(self, code_str, keywords):
        _id = str(uuid.uuid1())
        success = '{"code":200,"msg":"成功","data":exec_result}'
        err = '{"code":500,"msg":str(e),"data":None}'
        path = r'' + self.sandbox_path + ''
        _exec_code = f"""
try:
    import os
    env = dict(os.environ)
    for key in list(env.keys()):
        if key in os.environ and (key.startswith('MAXKB') or key.startswith('POSTGRES') or key.startswith('PG')):
            del os.environ[key]
    locals_v={'{}'}
    keywords={keywords}
    globals_v=globals()
    exec({dedent(code_str)!a}, globals_v, locals_v)
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
        if self.sandbox:
            subprocess_result = self._exec_sandbox(_exec_code, _id)
        else:
            subprocess_result = self._exec(_exec_code)
        if subprocess_result.returncode == 1:
            raise Exception(subprocess_result.stderr)
        cache = Cache(self.sandbox_path)
        result = cache.get(_id)
        cache.delete(_id)
        if result.get('code') == 200:
            return result.get('data')
        raise Exception(result.get('msg'))

    def _exec_sandbox(self, _code, _id):
        exec_python_file = f'{self.sandbox_path}/{_id}.py'
        with open(exec_python_file, 'w') as file:
            file.write(_code)
            os.system(f"chown {self.user}:{self.user} {exec_python_file}")
        kwargs = {'cwd': BASE_DIR}
        subprocess_result = subprocess.run(
            ['su', '-c', python_directory + ' ' + exec_python_file, self.user],
            text=True,
            capture_output=True, **kwargs)
        os.remove(exec_python_file)
        return subprocess_result

    @staticmethod
    def _exec(_code):
        return subprocess.run([python_directory, '-c', _code], text=True, capture_output=True)
