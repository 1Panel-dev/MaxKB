"""HTTP destination checks usable without Django inside an MCP worker."""

import ipaddress
import socket
import ssl

import anyio
import httpcore
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
            url.scheme not in ("http", "https") or not url.host or url.userinfo
            or url.fragment or "%" in url.host or "\\" in value
            or (url.port is not None and not 1 <= url.port <= 65535)
        ):
            raise ValueError("Invalid MCP server URL")
        return url
    except (httpx.InvalidURL, ValueError) as exc:
        raise ValueError("Invalid MCP server URL") from exc


def check_addresses(addresses, networks):
    if not addresses:
        raise MCPNetworkPolicyError("MCP server hostname has no addresses")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        # Do not let IPv6 transition mechanisms tunnel to restricted IPv4 hosts.
        transition = isinstance(ip, ipaddress.IPv6Address) and (
            ip.sixtofour is not None or ip.teredo is not None
            or ip in ipaddress.ip_network("64:ff9b::/96")
            or ip in ipaddress.ip_network("64:ff9b:1::/48")
        )
        public = ip.is_global and not ip.is_multicast and not transition
        if not public and not any(ip in network for network in networks):
            if ip in ipaddress.ip_network("198.18.0.0/15"):
                raise MCPNetworkPolicyError(
                    "MCP server resolved to a benchmark/Fake-IP address; configure the MCP domain "
                    "to return real DNS addresses (Surge: always-real-ip; Clash: fake-ip-filter)"
                )
            raise MCPNetworkPolicyError("MCP server address is not allowed by the network policy")


class MCPNetworkBackend(httpcore.AnyIOBackend):
    def __init__(self, networks):
        self.networks = networks

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        try:
            with anyio.fail_after(timeout):
                # Resolve again at connection time, validate EVERY result, then
                # connect to the numeric address. HTTP Host and TLS SNI remain
                # the original hostname in httpcore, including certificate checks.
                results = await anyio.getaddrinfo(host, port, type=socket.SOCK_STREAM)
                addresses = list(dict.fromkeys(item[4][0] for item in results))
                check_addresses(addresses, self.networks)
                for index, address in enumerate(addresses):
                    try:
                        return await super().connect_tcp(
                            address, port, timeout, local_address, socket_options
                        )
                    except (httpcore.ConnectError, httpcore.ConnectTimeout):
                        if index == len(addresses) - 1:
                            raise
        except TimeoutError as exc:
            raise httpcore.ConnectTimeout() from exc
        except OSError as exc:
            raise httpcore.ConnectError(str(exc)) from exc


class MCPTransport(httpx.AsyncHTTPTransport):
    def __init__(self, url, networks, internal=False):
        super().__init__(trust_env=False)
        self.url = parse_url(url)
        self.internal = internal
        # HTTPX 0.28 has no public network_backend argument. Keep its standard
        # response/error handling and replace only the pool's connection backend.
        self._pool._network_backend = MCPNetworkBackend(networks)

    async def handle_async_request(self, request):
        target = parse_url(str(request.url))
        if (target.scheme, target.host, target.port) != (self.url.scheme, self.url.host, self.url.port):
            raise ValueError("MCP requests must stay on the configured origin")
        if self.internal and target != self.url:
            raise ValueError("Internal MCP requests must use the generated endpoint")
        return await super().handle_async_request(request)


def http_client_factory(headers=None, timeout=None, auth=None, *, url, networks, internal=False):
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout if timeout is not None else httpx.Timeout(30, read=300),
        auth=auth,
        follow_redirects=False,
        trust_env=False,
        transport=MCPTransport(url, networks, internal),
    )
