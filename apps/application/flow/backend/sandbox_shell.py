import getpass
import os
import re

from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse

from maxkb.const import CONFIG

_enable_sandbox = bool(int(CONFIG.get('SANDBOX', 0)))
_run_user = 'sandbox' if _enable_sandbox else getpass.getuser()
_sandbox_python_sys_path = CONFIG.get_sandbox_python_package_paths().replace(',', ':')


class SandboxShellBackend(LocalShellBackend):
    def __init__(self, root_dir: str, **kwargs):
        if 'env' not in kwargs and not kwargs.get('inherit_env', False):
            env = os.environ.copy()
            path = env.get('PATH', '/usr/bin:/bin')

            # 将 sandbox 路径分解为列表，检查每个路径是否已存在
            existing_paths = set(path.split(os.pathsep))
            sandbox_paths = _sandbox_python_sys_path.split(os.pathsep) if _sandbox_python_sys_path else []
            new_paths = [p for p in sandbox_paths if p and p not in existing_paths]

            if new_paths:
                env['PATH'] = f"{os.pathsep.join(new_paths)}{os.pathsep}{path}"

            kwargs['env'] = env
        super().__init__(root_dir=root_dir, **kwargs)

    def _translate_virtual_paths(self, command: str) -> str:
        """Translate virtual absolute paths in the command to real filesystem paths.

        In virtual_mode=True, file tools (ls, glob, read_file) return virtual absolute
        paths like /skills/foo.py which map to {root_dir}/skills/foo.py.  But execute()
        runs a real shell where /skills/foo.py does not exist.  This method replaces
        any path token that exists under root_dir with its real path, while leaving
        genuine system paths (e.g. /usr/bin/python3) untouched.
        """
        root = str(self.cwd)

        def translate(m: re.Match) -> str:
            virtual_path = m.group(0)
            real_path = root + virtual_path
            return real_path if os.path.lexists(real_path) else virtual_path

        # Match absolute-path-like tokens: / followed by a non-whitespace sequence
        # that isn't clearly a flag (e.g. avoid matching -/something).
        # Only translate when virtual_mode is active.
        return re.sub(r'(?<![.\w\-])/[A-Za-z_][^\s\'"\\;|&><:,]*', translate, command)

    def execute(
            self,
            command: str,
            *,
            timeout: int | None = None,
    ) -> ExecuteResponse:
        if self.virtual_mode:
            command = self._translate_virtual_paths(command)

        if _enable_sandbox:
            # 用 runuser 在子进程里切换用户，父进程凭据保持不变，
            # 避免父进程 ruid/euid 不一致导致 execve 报 Permission denied
            command = f"runuser -u {_run_user} -- env -i LD_PRELOAD=/opt/maxkb-app/sandbox/lib/sandbox.so PATH=${{PATH}} {command}"
            # command = f"runuser -u {_run_user} -- env -i PATH=${{PATH}} {command}"

        # print(f"Executing command in sandbox: {command}")
        return super().execute(command=command, timeout=timeout)
