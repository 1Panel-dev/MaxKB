# coding=utf-8
import ast
import os
import pickle
import subprocess
import sys
from textwrap import dedent

import uuid_utils.compat as uuid

from maxkb.const import BASE_DIR, CONFIG
from maxkb.const import PROJECT_DIR

python_directory = sys.executable


class ToolExecutor:
    def __init__(self, sandbox=False):
        self.sandbox = sandbox
        if sandbox:
            self.sandbox_path = '/opt/maxkb-app/sandbox'
            self.user = 'sandbox'
        else:
            self.sandbox_path = os.path.join(PROJECT_DIR, 'data', 'sandbox')
            self.user = None
        self._createdir()
        if self.sandbox:
            os.system(f"chown -R {self.user}:root {self.sandbox_path}")
        self.banned_keywords = CONFIG.get("SANDBOX_PYTHON_BANNED_KEYWORDS", 'nothing_is_banned').split(',');

    def _createdir(self):
        old_mask = os.umask(0o077)
        try:
            os.makedirs(self.sandbox_path, 0o700, exist_ok=True)
            os.makedirs(os.path.join(self.sandbox_path, 'execute'), 0o700, exist_ok=True)
            os.makedirs(os.path.join(self.sandbox_path, 'result'), 0o700, exist_ok=True)
        finally:
            os.umask(old_mask)

    def exec_code(self, code_str, keywords):
        self.validate_banned_keywords(code_str)
        _id = str(uuid.uuid7())
        success = '{"code":200,"msg":"成功","data":exec_result}'
        err = '{"code":500,"msg":str(e),"data":None}'
        result_path = f'{self.sandbox_path}/result/{_id}.result'
        python_paths = CONFIG.get_sandbox_python_package_paths().split(',')
        _exec_code = f"""
try:
    import os
    import sys
    import pickle
    path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
    sys.path = [p for p in sys.path if p not in path_to_exclude]
    sys.path += {python_paths}
    env = dict(os.environ)
    for key in list(env.keys()):
        if key in os.environ and (key.startswith('MAXKB') or key.startswith('POSTGRES') or key.startswith('PG') or key.startswith('REDIS') or key == 'PATH'):
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

    def _generate_mcp_server_code(self, _code):
        self.validate_banned_keywords(_code)

        # 解析代码，提取导入语句和函数定义
        try:
            tree = ast.parse(_code)
        except SyntaxError:
            return _code

        imports = []
        functions = []
        other_code = []

        for node in tree.body:
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports.append(ast.unparse(node))
            elif isinstance(node, ast.FunctionDef):
                # 为函数添加 @mcp.tool() 装饰器
                func_code = ast.unparse(node)
                functions.append(f"@mcp.tool()\n{func_code}\n")
            else:
                other_code.append(ast.unparse(node))

        # 构建完整的 MCP 服务器代码
        code_parts = ["from mcp.server.fastmcp import FastMCP"]
        code_parts.extend(imports)
        code_parts.append(f"\nmcp = FastMCP(\"{uuid.uuid7()}\")\n")
        code_parts.extend(other_code)
        code_parts.extend(functions)
        code_parts.append("\nmcp.run(transport=\"stdio\")\n")

        return "\n".join(code_parts)

    def get_exec_code(self, code_str):
        python_paths = CONFIG.get_sandbox_python_package_paths().split(',')
        code = self._generate_mcp_server_code(code_str)
        return f"""
try:
    import os
    import sys
    import pickle
    path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
    sys.path = [p for p in sys.path if p not in path_to_exclude]
    sys.path += {python_paths}
    env = dict(os.environ)
    for key in list(env.keys()):
        if key in os.environ and (key.startswith('MAXKB') or key.startswith('POSTGRES') or key.startswith('PG') or key.startswith('REDIS') or key == 'PATH'):
            del os.environ[key]
    locals_v={'{}'}
    globals_v=globals()
    exec({dedent(code)!a}, globals_v, locals_v)
    f_name, f = locals_v.popitem()
    for local in locals_v:
        globals_v[local] = locals_v[local]
except Exception as e:
    pass
"""

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

    def validate_banned_keywords(self, code_str):
        matched = next((bad for bad in self.banned_keywords if bad in code_str), None)
        if matched:
            raise Exception(f"keyword '{matched}' is banned in the tool.")

    @staticmethod
    def _exec(_code):
        return subprocess.run([python_directory, '-c', _code], text=True, capture_output=True)
