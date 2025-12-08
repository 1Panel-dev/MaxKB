# coding=utf-8
import ast
import json
import os
import subprocess
import sys
from textwrap import dedent
import socket
import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from maxkb.const import BASE_DIR, CONFIG
from maxkb.const import PROJECT_DIR
from common.utils.logger import maxkb_logger

python_directory = sys.executable

class ToolExecutor:
    def __init__(self, sandbox=False):
        self.sandbox = sandbox
        if sandbox:
            self.sandbox_path = CONFIG.get("SANDBOX_HOME", '/opt/maxkb-app/sandbox')
            self.user = 'sandbox'
        else:
            self.sandbox_path = os.path.join(PROJECT_DIR, 'data', 'sandbox')
            self.user = None
        self._createdir()
        if self.sandbox:
            os.system(f"chown -R {self.user}:root {self.sandbox_path}")
        self.banned_keywords = CONFIG.get("SANDBOX_PYTHON_BANNED_KEYWORDS", 'nothing_is_banned').split(',');
        try:
            banned_hosts_file_path = f'{self.sandbox_path}/.SANDBOX_BANNED_HOSTS'
            if os.path.exists(banned_hosts_file_path):
                os.remove(banned_hosts_file_path)
            banned_hosts = CONFIG.get("SANDBOX_PYTHON_BANNED_HOSTS", '').strip()
            if banned_hosts:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                banned_hosts = f"{banned_hosts},{hostname},{local_ip}"
                with open(banned_hosts_file_path, "w") as f:
                    f.write(banned_hosts)
                os.chmod(banned_hosts_file_path, 0o644)
        except Exception as e:
            maxkb_logger.error(f'Failed to init SANDBOX_BANNED_HOSTS due to exception: {e}', exc_info=True)
            pass

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
    import json
    path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
    sys.path = [p for p in sys.path if p not in path_to_exclude]
    sys.path += {python_paths}
    locals_v={'{}'}
    keywords={keywords}
    globals_v={'{}'}
    exec({dedent(code_str)!a}, globals_v, locals_v)
    f_name, f = locals_v.popitem()
    for local in locals_v:
        globals_v[local] = locals_v[local]
    exec_result=f(**keywords)
    with open({result_path!a}, 'w') as file:
        file.write(json.dumps({success}, default=str))
except Exception as e:
    with open({result_path!a}, 'w') as file:
        file.write(json.dumps({err}))
"""
        if self.sandbox:
            subprocess_result = self._exec_sandbox(_exec_code, _id)
        else:
            subprocess_result = self._exec(_exec_code)
        if subprocess_result.returncode == 1:
            raise Exception(subprocess_result.stderr)
        with open(result_path, 'r') as file:
            result = json.loads(file.read())
        os.remove(result_path)
        if result.get('code') == 200:
            return result.get('data')
        raise Exception(result.get('msg'))

    def _generate_mcp_server_code(self, _code, params):
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
                # 修改函数参数以包含 params 中的默认值
                arg_names = [arg.arg for arg in node.args.args]

                # 为参数添加默认值，确保参数顺序正确
                defaults = []
                num_defaults = 0

                # 从后往前检查哪些参数有默认值
                for i, arg_name in enumerate(arg_names):
                    if arg_name in params:
                        num_defaults = len(arg_names) - i
                        break

                # 为有默认值的参数创建默认值列表
                if num_defaults > 0:
                    for i in range(len(arg_names) - num_defaults, len(arg_names)):
                        arg_name = arg_names[i]
                        if arg_name in params:
                            default_value = params[arg_name]
                            if isinstance(default_value, str):
                                defaults.append(ast.Constant(value=default_value))
                            elif isinstance(default_value, (int, float, bool)):
                                defaults.append(ast.Constant(value=default_value))
                            elif default_value is None:
                                defaults.append(ast.Constant(value=None))
                            else:
                                defaults.append(ast.Constant(value=str(default_value)))
                        else:
                            # 如果某个参数没有默认值，需要添加 None 占位
                            defaults.append(ast.Constant(value=None))

                    node.args.defaults = defaults

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

    def generate_mcp_server_code(self, code_str, params):
        python_paths = CONFIG.get_sandbox_python_package_paths().split(',')
        code = self._generate_mcp_server_code(code_str, params)
        return f"""
import os
import sys
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)

path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
sys.path = [p for p in sys.path if p not in path_to_exclude]
sys.path += {python_paths}
exec({dedent(code)!a})
"""

    def get_tool_mcp_config(self, code, params):
        code = self.generate_mcp_server_code(code, params)

        _id = uuid.uuid7()
        code_path = f'{self.sandbox_path}/execute/{_id}.py'
        with open(code_path, 'w') as f:
            f.write(code)
        if self.sandbox:
            os.system(f"chown {self.user}:root {code_path}")

            tool_config = {
                'command': 'su',
                'args': [
                    '-s', sys.executable,
                    '-c', f"exec(open('{code_path}', 'r').read())",
                    self.user,
                ],
                'cwd': self.sandbox_path,
                'env': {
                    'LD_PRELOAD': f'{self.sandbox_path}/sandbox.so',
                },
                'transport': 'stdio',
            }
        else:
            tool_config = {
                'command': sys.executable,
                'args': [code_path],
                'transport': 'stdio',
            }
        return _id, tool_config

    def _exec_sandbox(self, _code, _id):
        exec_python_file = f'{self.sandbox_path}/execute/{_id}.py'
        with open(exec_python_file, 'w') as file:
            file.write(_code)
            os.system(f"chown {self.user}:root {exec_python_file}")
        kwargs = {'cwd': BASE_DIR}
        kwargs['env'] = {
            'LD_PRELOAD': f'{self.sandbox_path}/sandbox.so',
        }
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

    def validate_mcp_transport(self, code_str):
        servers = json.loads(code_str)
        for server, config in servers.items():
            if config.get('transport') not in ['sse', 'streamable_http']:
                raise Exception(_('Only support transport=sse or transport=streamable_http'))

    @staticmethod
    def _exec(_code):
        return subprocess.run([python_directory, '-c', _code], text=True, capture_output=True)
