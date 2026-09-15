"""Build fixed stdio worker connections; user configuration never selects code."""

import json
import pwd
import sys
from datetime import timedelta
from importlib.machinery import PathFinder
from pathlib import Path

from mcp.types import Implementation

from maxkb.const import CONFIG


BOOTSTRAP_KEY = "maxkbSandbox"
REMOTE_FIELDS = {"transport", "url", "headers", "timeout", "sse_read_timeout", "terminate_on_close"}


def sandbox_settings():
    if not sys.platform.startswith("linux") or not bool(int(CONFIG.get("SANDBOX", 1))):
        raise ValueError("External MCP requires an enabled Linux sandbox")
    account = pwd.getpwnam("sandbox")
    sandbox_home = Path(CONFIG.get("SANDBOX_HOME", "/opt/maxkb-app/sandbox"))
    library = sandbox_home / "lib/sandbox.so"
    if not library.is_file() or not library.with_name(".sandbox.conf").is_file():
        raise ValueError("MCP sandbox library or configuration is missing")
    return {
        "uid": account.pw_uid,
        "gid": account.pw_gid,
        "library": str(library),
        "cwd": str(sandbox_home),
        "python_paths": CONFIG.get_sandbox_python_package_paths().split(","),
        "memory_mb": int(CONFIG.get("SANDBOX_PYTHON_PROCESS_LIMIT_MEM_MB", "256")),
        "cpu_cores": int(CONFIG.get("SANDBOX_PYTHON_PROCESS_LIMIT_CPU_CORES", "1")),
        "timeout": int(CONFIG.get("SANDBOX_PYTHON_PROCESS_LIMIT_TIMEOUT_SECONDS", "3600")),
    }


def sandbox_connection(config):
    settings = sandbox_settings()
    # Release builds replace source files with adjacent, sourceless .pyc files.
    # Search only our installed directory, never a user-controlled module path.
    worker = PathFinder.find_spec("sandbox_worker", [str(Path(__file__).parent)])
    if worker is None or worker.origin is None or Path(worker.origin).suffix not in (".py", ".pyc"):
        raise RuntimeError("MCP sandbox worker is missing or has an unsupported format")
    # Only transport data goes to the remote client. In particular, ignore user
    # command/env/factory/session_kwargs fields and never deserialize Python code.
    remote = {key: value for key, value in config.items() if key in REMOTE_FIELDS}
    bootstrap = {"connection": remote}
    # Check serializability before launching, and detach from mutable input.
    bootstrap = json.loads(json.dumps(bootstrap, allow_nan=False))
    return {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-I", worker.origin],
        "cwd": settings["cwd"],
        "env": {
            "LD_PRELOAD": settings["library"],
            "MAXKB_MCP_WORKER_SETTINGS": json.dumps(settings),
        },
        "session_kwargs": {
            "read_timeout_seconds": timedelta(seconds=settings["timeout"]),
            # This field travels only over the child's stdio pipe. The worker
            # removes it before forwarding initialize to the remote server.
            "client_info": Implementation(name="maxkb-sandbox", version="1", **{BOOTSTRAP_KEY: bootstrap}),
        },
    }
