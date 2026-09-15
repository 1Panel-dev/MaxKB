"""HTTP request safeguards; address access is enforced by sandbox.so."""

import socket
import ssl

import httpx


class MCPNetworkPolicyError(ValueError):
    """Locally generated, credential-free policy failure safe to report."""


def sandbox_failure_message(error):
    # SDK exception groups and chained HTTP errors can embed credentials. Only
    # report our own policy text, a numeric HTTP status, or a fixed description.
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
        if isinstance(current, MCPNetworkPolicyError):
            return str(current)
    for current in errors:
        if isinstance(current, httpx.HTTPStatusError):
            status = current.response.status_code
            if 300 <= status < 400:
                return "MCP endpoint returned a redirect; configure its final URL"
            return f"MCP endpoint returned HTTP {status}; check endpoint and credentials"
    for exception_type, message in (
        (ssl.SSLCertVerificationError, "MCP TLS certificate verification failed"),
        (socket.gaierror, "MCP hostname resolution failed; check container DNS"),
        (PermissionError, "MCP access denied; check sandbox file and network policy"),
        ((httpx.TimeoutException, TimeoutError), "MCP connection timed out"),
        (httpx.ConnectError, "MCP connection failed; check container connectivity and sandbox network policy"),
    ):
        if any(isinstance(current, exception_type) for current in errors):
            return message
    return "MCP session failed; check endpoint, sandbox setup and network policy"


def parse_url(value):
    if not isinstance(value, str) or not value or any(ord(c) <= 32 for c in value):
        raise ValueError("Invalid MCP server URL")
    try:
        url = httpx.URL(value)
        if (
            url.scheme not in ("http", "https")
            or not url.host
            or url.userinfo
            or url.fragment
            or "%" in url.host
            or "\\" in value
            or (url.port is not None and not 1 <= url.port <= 65535)
        ):
            raise ValueError("Invalid MCP server URL")
        return url
    except (httpx.InvalidURL, ValueError) as exc:
        raise ValueError("Invalid MCP server URL") from exc


class MCPTransport(httpx.AsyncHTTPTransport):
    def __init__(self, url, internal=False):
        super().__init__(trust_env=False)
        self.url = parse_url(url)
        self.internal = internal
        # Keep the standard resolver/socket backend so sandbox.so checks both
        # the requested hostname and the actual address passed to connect().

    async def handle_async_request(self, request):
        target = parse_url(str(request.url))
        if (target.scheme, target.host, target.port) != (self.url.scheme, self.url.host, self.url.port):
            raise MCPNetworkPolicyError("MCP requests must stay on the configured origin")
        if self.internal and target != self.url:
            raise MCPNetworkPolicyError("Internal MCP requests must use the generated endpoint")
        return await super().handle_async_request(request)


def http_client_factory(headers=None, timeout=None, auth=None, *, url, internal=False):
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout if timeout is not None else httpx.Timeout(30, read=300),
        auth=auth,
        follow_redirects=False,
        trust_env=False,
        transport=MCPTransport(url, internal),
    )
