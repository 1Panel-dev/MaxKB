"""Fixed Linux entry point for the stdio-to-HTTP MCP sandbox proxy."""

import ctypes
from contextlib import contextmanager
import errno
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import pwd
import resource
import signal
import socket
import struct
import sys


class MCPWorkerFailure(Exception):
    """A failure whose message was sanitized by the fixed network module."""


class DlInfo(ctypes.Structure):
    _fields_ = [
        ("filename", ctypes.c_char_p),
        ("base", ctypes.c_void_p),
        ("symbol", ctypes.c_char_p),
        ("address", ctypes.c_void_p),
    ]


class AddrInfo(ctypes.Structure):
    pass


AddrInfo._fields_ = [
    ("flags", ctypes.c_int),
    ("family", ctypes.c_int),
    ("socktype", ctypes.c_int),
    ("protocol", ctypes.c_int),
    ("addrlen", ctypes.c_uint),
    ("addr", ctypes.c_void_p),
    ("canonname", ctypes.c_char_p),
    ("next", ctypes.POINTER(AddrInfo)),
]


@contextmanager
def quiet_probe():
    # The C hook logs denied connections. Suppress only our synthetic startup
    # probes, before any remote connection or concurrent task has been started.
    saved = os.dup(2)
    try:
        with open(os.devnull, "w") as sink:
            os.dup2(sink.fileno(), 2)
            yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)


class SandboxNetworkCheck:
    """Verify the existing interposer without requiring a new C export."""

    def __init__(self, library):
        # Resolve process-global symbols only: loading a library here would not
        # prove LD_PRELOAD actually installed the interposed network functions.
        process = ctypes.CDLL(None, use_errno=True)
        dladdr = process.dladdr
        dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
        dladdr.restype = ctypes.c_int
        self.connect = process.connect
        self.connect.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint]
        self.connect.restype = ctypes.c_int
        self.getaddrinfo = process.getaddrinfo
        self.getaddrinfo.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(AddrInfo),
            ctypes.POINTER(ctypes.POINTER(AddrInfo)),
        ]
        self.getaddrinfo.restype = ctypes.c_int
        self.freeaddrinfo = process.freeaddrinfo
        self.freeaddrinfo.argtypes = [ctypes.POINTER(AddrInfo)]
        self.freeaddrinfo.restype = None
        for function in (self.connect, self.getaddrinfo):
            info = DlInfo()
            if not dladdr(ctypes.cast(function, ctypes.c_void_p), ctypes.byref(info)) or not info.filename:
                raise RuntimeError("Cannot locate MCP sandbox network hooks")
            loaded_path = Path(os.fsdecode(info.filename))
            if not os.path.samefile(loaded_path, library):
                raise RuntimeError("MCP sandbox network hooks are not preloaded")
            self.policy_path = loaded_path.with_name(".sandbox.conf")

    def verify(self):
        rules = ""
        # Read as the sandbox user, from the same path used by the C interposer.
        # Reject a truncated policy rather than relying on its first 511 bytes.
        for line in self.policy_path.read_text().splitlines(keepends=True):
            key, separator, value = line.partition("=")
            if separator and key.strip() == "SANDBOX_PYTHON_BANNED_HOSTS":
                if len(line.encode()) > 511:
                    raise RuntimeError("MCP sandbox network policy is too long")
                rules = value.strip()
        if not rules:
            raise RuntimeError("MCP sandbox network policy is empty")
        for rule in filter(None, (value.strip() for value in rules.split(","))):
            try:
                ip = ipaddress.ip_network(rule, strict=False).network_address
            except ValueError:
                # Numeric-only flags prevent this self-check from sending DNS
                # traffic, even if the rule is ineffective or the hook is broken.
                hints = AddrInfo(flags=socket.AI_NUMERICHOST | socket.AI_NUMERICSERV)
                result = ctypes.POINTER(AddrInfo)()
                ctypes.set_errno(0)
                with quiet_probe():
                    status = self.getaddrinfo(rule.encode(), b"0", ctypes.byref(hints), ctypes.byref(result))
                error = ctypes.get_errno()
                if result:
                    self.freeaddrinfo(result)
                if status == socket.EAI_SYSTEM and error == errno.EACCES:
                    return
            else:
                if ip.version == 4:
                    address = struct.pack("=H", socket.AF_INET) + b"\0\0" + ip.packed + b"\0" * 8
                else:
                    address = struct.pack("=H", socket.AF_INET6) + b"\0" * 6 + ip.packed + b"\0" * 4
                buffer = ctypes.create_string_buffer(address)
                ctypes.set_errno(0)
                # -1 can never send a packet: libc returns EBADF, while the
                # active sandbox must reject a configured banned IP with EACCES.
                with quiet_probe():
                    status = self.connect(-1, buffer, len(address))
                if status == -1 and ctypes.get_errno() == errno.EACCES:
                    return
        raise RuntimeError("MCP sandbox network policy self-check failed")


def enter_sandbox(settings):
    if not sys.platform.startswith("linux"):
        raise RuntimeError("MCP sandbox requires Linux")
    account = pwd.getpwnam("sandbox")
    if settings["uid"] != account.pw_uid or settings["gid"] != account.pw_gid or account.pw_uid == 0:
        raise RuntimeError("Invalid MCP sandbox identity")
    network_check = SandboxNetworkCheck(settings["library"])
    timeout = settings["timeout"]
    memory = settings["memory_mb"] * 1024 * 1024
    cores = settings["cpu_cores"]
    if timeout <= 0 or memory <= 0 or cores <= 0:
        raise RuntimeError("Invalid MCP sandbox resource limits")
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:cores])
    # The SDK closes stdin, then terminates/kills the child when a session ends.
    # This independent wall deadline also bounds a hung handshake or orphan.
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.alarm(timeout)
    os.setgroups([])
    os.setgid(account.pw_gid)
    os.setuid(account.pw_uid)
    os.environ.clear()
    if os.getuid() != account.pw_uid or os.geteuid() != account.pw_uid:
        raise RuntimeError("MCP sandbox identity was not applied")
    network_check.verify()


def main():
    settings = json.loads(os.environ.pop("MAXKB_MCP_WORKER_SETTINGS"))
    # Load only fixed, installed modules before dropping access to the app tree.
    # Neither module imports Django nor reads the application configuration.
    modules = {}
    for name in ("mcp_network", "mcp_sandbox_proxy"):
        path = Path(__file__).with_name(name + ".py")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    # Remove the application directory while retaining approved package paths.
    app_path = str(Path(__file__).resolve().parents[2])
    sys.path = [p for p in sys.path if p != app_path]
    sys.path.extend(p for p in settings["python_paths"] if p and p not in sys.path)
    enter_sandbox(settings)
    try:
        modules["mcp_sandbox_proxy"].run(modules["mcp_network"].http_client_factory)
    except Exception as exc:
        raise MCPWorkerFailure(modules["mcp_network"].sandbox_failure_message(exc)) from None


if __name__ == "__main__":
    try:
        main()
    except MCPWorkerFailure as exc:
        sys.stderr.write(f"MCP sandbox worker failed: {exc}.\n")
        sys.exit(1)
    except BaseException:
        # URLs/headers may contain secrets: keep failures off stdout and do not
        # dump exceptions or bootstrap data inherited from the remote SDK.
        sys.stderr.write("MCP sandbox worker failed; check sandbox setup and network policy.\n")
        sys.exit(1)
