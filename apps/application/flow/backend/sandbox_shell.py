import getpass
import os
import re
import shlex

from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse

from common.utils.logger import maxkb_logger
from maxkb.const import CONFIG

_enable_sandbox = bool(int(CONFIG.get("SANDBOX", 0)))
_run_user = "sandbox" if _enable_sandbox else getpass.getuser()
_sandbox_python_sys_path = CONFIG.get_sandbox_python_package_paths().replace(",", ":")


class SandboxShellBackend(LocalShellBackend):
    def __init__(self, root_dir: str, **kwargs):
        if "env" not in kwargs and not kwargs.get("inherit_env", False):
            env = os.environ.copy()
            python_path = env.get("PYTHONPATH", "")

            # 将 sandbox Python 包路径分解为列表，检查每个路径是否已存在
            existing_paths = set(python_path.split(os.pathsep))
            sandbox_paths = _sandbox_python_sys_path.split(os.pathsep) if _sandbox_python_sys_path else []
            new_paths = [p for p in sandbox_paths if p and p not in existing_paths]

            if new_paths:
                env["PYTHONPATH"] = (
                    f"{os.pathsep.join(new_paths)}{os.pathsep}{python_path}"
                    if python_path
                    else os.pathsep.join(new_paths)
                )

            kwargs["env"] = env
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

    def _consume_group(self, command: str, start_index: int) -> tuple[str, int]:
        current = []
        in_single_quote = False
        in_double_quote = False
        in_backticks = False
        escaped = False
        substitution_depth = 0
        group_depth = 1
        index = start_index + 1

        while index < len(command):
            char = command[index]

            if escaped:
                current.append(char)
                escaped = False
                index += 1
                continue

            if char == "\\" and not in_single_quote:
                current.append(char)
                escaped = True
                index += 1
                continue

            if char == "`" and not in_single_quote:
                in_backticks = not in_backticks
                current.append(char)
                index += 1
                continue

            if in_backticks:
                current.append(char)
                index += 1
                continue

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current.append(char)
                index += 1
                continue

            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current.append(char)
                index += 1
                continue

            if in_single_quote or in_double_quote:
                current.append(char)
                index += 1
                continue

            if command.startswith("$(", index):
                substitution_depth += 1
                current.append("$(")
                index += 2
                continue

            if substitution_depth:
                if char == ")":
                    substitution_depth -= 1
                current.append(char)
                index += 1
                continue

            if char == "(":
                group_depth += 1
                current.append(char)
                index += 1
                continue

            if char == ")":
                group_depth -= 1
                if group_depth == 0:
                    return "".join(current).strip(), index + 1
                current.append(char)
                index += 1
                continue

            current.append(char)
            index += 1

        raise ValueError("unclosed command group")

    def _append_pending_command_part(self, parts: list[str | tuple[str, str]], current: list[str]) -> None:
        part = "".join(current).strip()
        if part:
            parts.append(part)
            return

        if not parts:
            parts.append("")
            return

        last_part = parts[-1]
        if isinstance(last_part, str) and last_part in {";", "&&", "||", "|", "&"}:
            parts.append("")

    def _split_shell_command_list(self, command: str) -> list[str | tuple[str, str]]:
        parts = []
        current = []
        in_single_quote = False
        in_double_quote = False
        in_backticks = False
        escaped = False
        substitution_depth = 0
        index = 0

        while index < len(command):
            char = command[index]

            if escaped:
                current.append(char)
                escaped = False
                index += 1
                continue

            if char == "\\" and not in_single_quote:
                current.append(char)
                escaped = True
                index += 1
                continue

            if char == "`" and not in_single_quote:
                in_backticks = not in_backticks
                current.append(char)
                index += 1
                continue

            if in_backticks:
                current.append(char)
                index += 1
                continue

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current.append(char)
                index += 1
                continue

            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current.append(char)
                index += 1
                continue

            if not in_single_quote and not in_double_quote:
                if command.startswith("$(", index):
                    substitution_depth += 1
                    current.append("$(")
                    index += 2
                    continue

                if substitution_depth:
                    if char == ")":
                        substitution_depth -= 1
                    current.append(char)
                    index += 1
                    continue

                if char == "(" and not "".join(current).strip():
                    group_content, index = self._consume_group(command, index)
                    parts.append(("group", group_content))
                    current = []
                    continue

                if command.startswith("&&", index) or command.startswith("||", index):
                    self._append_pending_command_part(parts, current)
                    parts.append(command[index : index + 2])
                    current = []
                    index += 2
                    continue

                if char in {";", "|", "&"}:
                    self._append_pending_command_part(parts, current)
                    parts.append(char)
                    current = []
                    index += 1
                    continue

                if char == "\n":
                    self._append_pending_command_part(parts, current)
                    parts.append(";")
                    current = []
                    index += 1
                    continue

            current.append(char)
            index += 1

        self._append_pending_command_part(parts, current)
        return parts

    def _build_sandbox_command(self, command: str) -> str:
        prefix = (
            "env -i LD_PRELOAD=/opt/maxkb-app/sandbox/lib/sandbox.so "
            f'PATH="${{PATH}}" PYTHONPATH="${{PYTHONPATH}}" gosu {_run_user} '
        )
        parts = self._split_shell_command_list(command)
        sandboxed_parts = []
        expect_command = True

        for part in parts:
            if expect_command:
                if isinstance(part, tuple):
                    group_kind, group_content = part
                    if group_kind != "group":
                        raise ValueError(f"unsupported command part: {group_kind}")
                    if not group_content:
                        raise ValueError("empty command group")
                    sandboxed_parts.append(f"( {self._build_sandbox_command(group_content)} )")
                elif not part:
                    raise ValueError("empty command")
                else:
                    tokens = shlex.split(part)
                    if not tokens:
                        raise ValueError("empty command")
                    sandboxed_parts.append(prefix + " ".join(shlex.quote(token) for token in tokens))
            else:
                if part not in {";", "&&", "||", "|", "&"}:
                    raise ValueError(f"unsupported shell operator: {part}")
                sandboxed_parts.append(part)

            expect_command = not expect_command

        if expect_command:
            raise ValueError("command cannot end with a shell operator")

        return " ".join(sandboxed_parts)

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
            try:
                # 将命令列表拆成多个简单命令，并分别在 sandbox 用户下执行。
                # 每个简单命令仍按 argv 重新 quote，避免 $()、反引号等在父 shell 中展开。
                command = self._build_sandbox_command(command)
            except ValueError as e:
                return ExecuteResponse(output=f"Invalid command: {e}", exit_code=1)
            # command = f"runuser -u {_run_user} -- env -i PATH=${{PATH}} {command}"

        maxkb_logger.info(f"Executing command in sandbox: {command}")
        return super().execute(command=command, timeout=timeout)
