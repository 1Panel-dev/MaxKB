# coding=utf-8
import ast
import base64
import gzip
import json
import os
import socket
import subprocess
import sys
import signal
import time
import uuid_utils.compat as uuid
from common.utils.logger import maxkb_logger
from django.utils.translation import gettext_lazy as _
from maxkb.const import BASE_DIR, CONFIG
from maxkb.const import PROJECT_DIR
from textwrap import dedent

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
        self.sandbox_so_path = f'{self.sandbox_path}/lib/sandbox.so'
        self.process_timeout_seconds = int(CONFIG.get("SANDBOX_PYTHON_PROCESS_TIMEOUT_SECONDS", '3600'))
        try:
            self._init_sandbox_dir()
        except Exception as e:
            # 本机忽略异常，容器内不忽略
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if self.sandbox:
                raise e

    def _init_sandbox_dir(self):
        if not self.sandbox:
            # 不是sandbox就不初始化目录
            return
        try:
            # 只初始化一次
            fd = os.open(os.path.join(PROJECT_DIR, 'tmp', 'tool_executor_init_dir.lock'),
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            # 文件已存在 → 已初始化过
            return
        maxkb_logger.debug("init dir")
        try:
            os.system("chmod -R g-rwx /dev/shm /dev/mqueue")
            os.system("chmod o-rwx /run/postgresql")
        except Exception as e:
            maxkb_logger.warning(f'Exception: {e}', exc_info=True)
            pass
        if CONFIG.get("SANDBOX_TMP_DIR_ENABLED", '0') == "1":
            os.system("chmod g+rwx /tmp")
        # 初始化sandbox配置文件
        sandbox_lib_path = os.path.dirname(self.sandbox_so_path)
        sandbox_conf_file_path = f'{sandbox_lib_path}/.sandbox.conf'
        if os.path.exists(sandbox_conf_file_path):
            os.remove(sandbox_conf_file_path)
        allow_subprocess = CONFIG.get("SANDBOX_PYTHON_ALLOW_SUBPROCESS", '0')
        banned_hosts = CONFIG.get("SANDBOX_PYTHON_BANNED_HOSTS", '').strip()
        if banned_hosts:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            banned_hosts = f"{banned_hosts},{hostname},{local_ip}"
        with open(sandbox_conf_file_path, "w") as f:
            f.write(f"SANDBOX_PYTHON_BANNED_HOSTS={banned_hosts}\n")
            f.write(f"SANDBOX_PYTHON_ALLOW_SUBPROCESS={allow_subprocess}\n")
        os.system(f"chmod -R 550 {self.sandbox_path}")

    def exec_code(self, code_str, keywords, function_name=None):
        _id = str(uuid.uuid7())
        success = '{"code":200,"msg":"成功","data":exec_result}'
        err = '{"code":500,"msg":str(e),"data":None}'
        action_function = f'({function_name !a}, locals_v.get({function_name !a}))' if function_name else 'locals_v.popitem()'
        python_paths = CONFIG.get_sandbox_python_package_paths().split(',')
        _exec_code = f"""
try:
    import os, sys, json, base64, builtins
    path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
    sys.path = [p for p in sys.path if p not in path_to_exclude]
    sys.path += {python_paths}
    locals_v={'{}'}
    keywords={keywords}
    globals_v={'{}'}
    os.environ.clear()
    exec({dedent(code_str)!a}, globals_v, locals_v)
    f_name, f = {action_function}
    for local in locals_v:
        globals_v[local] = locals_v[local]
    exec_result=f(**keywords)
    builtins.print("\\n{_id}:"+base64.b64encode(json.dumps({success}, default=str).encode()).decode())
except Exception as e:
    builtins.print("\\n{_id}:"+base64.b64encode(json.dumps({err}, default=str).encode()).decode())
"""
        if self.sandbox:
            subprocess_result = self._exec_sandbox(_exec_code)
        else:
            subprocess_result = self._exec(_exec_code)
        if subprocess_result.returncode == 1:
            raise Exception(subprocess_result.stderr)
        lines = subprocess_result.stdout.splitlines()
        result_line = [line for line in lines if line.startswith(_id)]
        if not result_line:
            maxkb_logger.error("\n".join(lines))
            raise Exception("No result found.")
        result = json.loads(base64.b64decode(result_line[-1].split(":", 1)[1]).decode())
        if result.get('code') == 200:
            return result.get('data')
        raise Exception(result.get('msg'))

    def _generate_mcp_server_code(self, _code, params):
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
import os, sys, logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
path_to_exclude = ['/opt/py3/lib/python3.11/site-packages', '/opt/maxkb-app/apps']
sys.path = [p for p in sys.path if p not in path_to_exclude]
sys.path += {python_paths}
os.environ.clear()
exec({dedent(code)!a})
"""

    def get_tool_mcp_config(self, code, params):
        _code = self.generate_mcp_server_code(code, params)
        maxkb_logger.debug(f"Python code of mcp tool: {_code}")
        compressed_and_base64_encoded_code_str = base64.b64encode(gzip.compress(_code.encode())).decode()
        if self.sandbox:
            tool_config = {
                'command': 'su',
                'args': [
                    '-s', sys.executable,
                    '-c',
                    f'import base64,gzip; exec(gzip.decompress(base64.b64decode(\'{compressed_and_base64_encoded_code_str}\')).decode())',
                    self.user,
                ],
                'cwd': self.sandbox_path,
                'env': {
                    'LD_PRELOAD': self.sandbox_so_path,
                },
                'transport': 'stdio',
            }
        else:
            tool_config = {
                'command': sys.executable,
                'args': [
                    '-c',
                    f'import base64,gzip; exec(gzip.decompress(base64.b64decode(\'{compressed_and_base64_encoded_code_str}\')).decode())',
                ],
                'transport': 'stdio',
            }
        return tool_config

    def _exec_sandbox(self, _code):
        kwargs = {'cwd': BASE_DIR, 'env': {
            'LD_PRELOAD': self.sandbox_so_path,
        }}
        maxkb_logger.debug(f"Sandbox execute code: {_code}")
        compressed_and_base64_encoded_code_str = base64.b64encode(gzip.compress(_code.encode())).decode()
        cmd = [
            'su', '-s', python_directory, '-c',
            f'import base64,gzip; exec(gzip.decompress(base64.b64decode(\'{compressed_and_base64_encoded_code_str}\')).decode())',
            self.user
        ]
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                **kwargs,
                start_new_session=True
            )
            proc.wait(timeout=self.process_timeout_seconds)
            return subprocess.CompletedProcess(
                proc.args,
                proc.returncode,
                proc.stdout.read(),
                proc.stderr.read()
            )
        except subprocess.TimeoutExpired:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGTERM) #温和终止
            time.sleep(1) #留出短暂时间让进程清理
            if proc.poll() is None: #如果仍未终止，强制终止
                os.killpg(pgid, signal.SIGKILL)
            proc.wait()
            raise Exception(_(f"Process execution timed out after {self.process_timeout_seconds} seconds."))

    def validate_mcp_transport(self, code_str):
        servers = json.loads(code_str)
        for server, config in servers.items():
            if config.get('transport') not in ['sse', 'streamable_http']:
                raise Exception(_('Only support transport=sse or transport=streamable_http'))

    @staticmethod
    def _exec(_code):
        return subprocess.run([python_directory, '-c', _code], text=True, capture_output=True)
