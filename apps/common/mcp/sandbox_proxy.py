"""Forward MCP messages without converting tools, results or notifications."""

from contextlib import asynccontextmanager
import logging
import os
import socket
import ssl
import sys

import anyio
import httpx
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client
from mcp.server.stdio import stdio_server
from mcp.shared._httpx_utils import create_mcp_http_client
from mcp.types import JSONRPCRequest


def sandbox_failure_message(error):
    # SDK exception groups and chained HTTP errors can embed credentials. Only
    # report numeric HTTP statuses or fixed descriptions, never exception text.
    errors, pending, seen = [], [error], set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        errors.append(current)
        if isinstance(current, BaseExceptionGroup):
            pending.extend(current.exceptions)
        if current.__cause__ is not None:
            pending.append(current.__cause__)
    for current in errors:
        if isinstance(current, httpx.HTTPStatusError):
            return f"MCP endpoint returned HTTP {current.response.status_code}; check endpoint and credentials"
    for exception_type, message in (
        (ssl.SSLCertVerificationError, "MCP TLS certificate verification failed"),
        (socket.gaierror, "MCP hostname resolution failed; check container DNS"),
        (PermissionError, "MCP access denied; check sandbox file and network policy"),
        ((httpx.TimeoutException, TimeoutError), "MCP connection timed out"),
        (httpx.TooManyRedirects, "MCP endpoint returned too many redirects"),
        (httpx.ConnectError, "MCP connection failed; check container connectivity and sandbox network policy"),
    ):
        if any(isinstance(current, exception_type) for current in errors):
            return message
    return "MCP session failed; check endpoint, sandbox setup and network policy"


class PipeInput:
    """Cancellable pipe reads; a blocked readline thread would delay shutdown."""

    def __init__(self):
        self.fd = sys.stdin.fileno()
        os.set_blocking(self.fd, False)
        self.buffer = b""

    def __aiter__(self):
        return self

    async def __anext__(self):
        while b"\n" not in self.buffer:
            await anyio.wait_readable(self.fd)
            try:
                chunk = os.read(self.fd, 65536)
            except BlockingIOError:
                continue
            if not chunk:
                raise StopAsyncIteration
            self.buffer += chunk
            if len(self.buffer) > 32 * 1024 * 1024:
                raise ValueError("MCP message exceeds sandbox limit")
        line, self.buffer = self.buffer.split(b"\n", 1)
        return line.decode("utf-8")


class PipeOutput:
    def __init__(self):
        self.fd = sys.stdout.fileno()
        os.set_blocking(self.fd, False)

    async def write(self, value):
        remaining = value.encode("utf-8")
        while remaining:
            await anyio.wait_writable(self.fd)
            try:
                written = os.write(self.fd, remaining)
            except BlockingIOError:
                continue
            remaining = remaining[written:]

    async def flush(self):
        pass


def extract_bootstrap(message):
    request = message.message.root
    if not isinstance(request, JSONRPCRequest) or request.method != "initialize":
        raise ValueError("MCP sandbox requires initialize first")
    params = dict(request.params or {})
    client_info = dict(params.get("clientInfo") or {})
    bootstrap = client_info.pop("maxkbSandbox", None)
    if not isinstance(bootstrap, dict):
        raise ValueError("Missing MCP sandbox bootstrap")
    params["clientInfo"] = client_info
    request.params = params
    return bootstrap


@asynccontextmanager
async def remote_transport(bootstrap):
    config = bootstrap["connection"]
    if config.get("transport") not in ("sse", "streamable_http"):
        raise ValueError("Unsupported external MCP transport")
    timeout = config.get("timeout", 5 if config["transport"] == "sse" else 30)
    read_timeout = config.get("sse_read_timeout", 300)
    if config["transport"] == "sse":
        async with sse_client(
            config["url"], headers=config.get("headers"), timeout=timeout,
            sse_read_timeout=read_timeout,
        ) as streams:
            yield streams
    else:
        async with create_mcp_http_client(
            headers=config.get("headers"), timeout=httpx.Timeout(timeout, read=read_timeout),
        ) as client:
            async with streamable_http_client(
                config["url"], http_client=client, terminate_on_close=config.get("terminate_on_close", True),
            ) as (read, write, _):
                yield read, write


async def forward(source, destination, cancel_scope):
    try:
        async for message in source:
            if isinstance(message, Exception):
                raise message
            await destination.send(message)
    finally:
        cancel_scope.cancel()


async def proxy():
    async with stdio_server(stdin=PipeInput(), stdout=PipeOutput()) as (local_read, local_write):
        with anyio.fail_after(30):
            first = await local_read.receive()
            bootstrap = extract_bootstrap(first)
        async with remote_transport(bootstrap) as (remote_read, remote_write):
            async with anyio.create_task_group() as tasks:
                tasks.start_soon(forward, remote_read, local_write, tasks.cancel_scope)
                await remote_write.send(first)
                tasks.start_soon(forward, local_read, remote_write, tasks.cancel_scope)


def run():
    # Remote SDK exceptions may contain authorization headers or URL parameters.
    logging.disable(logging.CRITICAL)
    anyio.run(proxy)
