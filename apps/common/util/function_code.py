# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_code.py
    @date：2024/8/7 16:11
    @desc:
"""
import os
import pickle
import subprocess
import sys
import uuid
from textwrap import dedent

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
            os.system(f"chown -R {self.user}:root {self.sandbox_path}")

    def _createdir(self):
        old_mask = os.umask(0o077)
        try:
            os.makedirs(self.sandbox_path, 0o700, exist_ok=True)
            os.makedirs(os.path.join(self.sandbox_path, 'execute'), 0o700, exist_ok=True)
            os.makedirs(os.path.join(self.sandbox_path, 'result'), 0o700, exist_ok=True)
        finally:
            os.umask(old_mask)

    def exec_code(self, code_str, keywords):
        _id = str(uuid.uuid1())
        success = '{"code":200,"msg":"成功","data":exec_result}'
        err = '{"code":500,"msg":str(e),"data":None}'
        result_path = f'{self.sandbox_path}/result/{_id}.result'
        _exec_code = f"""
try:
    import os
    import pickle
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
    with open({result_path!a}, 'wb') as file:
        file.write(pickle.dumps({success}))
except Exception as e:
    with open({result_path!a}, 'wb') as file:
        file.write(pickle.dumps({err}))
"""
        if self.sandbox:
            subprocess_result = self._exec_sandbox(_exec_code, _id)
        else:
            subprocess_result = self._exec(_exec_code)
        if subprocess_result.returncode == 1:
            raise Exception(subprocess_result.stderr)
        with open(result_path, 'rb') as file:
            result = pickle.loads(file.read())
        os.remove(result_path)
        if result.get('code') == 200:
            return result.get('data')
        raise Exception(result.get('msg'))

    def _exec_sandbox(self, _code, _id):
        exec_python_file = f'{self.sandbox_path}/execute/{_id}.py'
        with open(exec_python_file, 'w') as file:
            file.write(_code)
            os.system(f"chown {self.user}:root {exec_python_file}")
        kwargs = {'cwd': BASE_DIR}
        subprocess_result = subprocess.run(
            ['su', '-s', python_directory, '-c', "exec(open('" + exec_python_file + "').read())", self.user],
            text=True,
            capture_output=True, **kwargs)
        os.remove(exec_python_file)
        return subprocess_result

    @staticmethod
    def _exec(_code):
        return subprocess.run([python_directory, '-c', _code], text=True, capture_output=True)
