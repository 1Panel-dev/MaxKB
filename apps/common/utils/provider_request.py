# coding=utf-8
"""HTTP transport for configurable model endpoints, including private deployments."""
import ipaddress
import socket
from urllib.parse import urlsplit

import requests
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.exceptions import NewConnectionError


_PRIVATE_NETWORKS = tuple(map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7")))
_TRANSLATION_NETWORKS = tuple(map(ipaddress.ip_network, ("64:ff9b::/96", "64:ff9b:1::/48")))
_METADATA_NETWORK = ipaddress.ip_network("fd00:ec2::/32")


def _validate_url(url):
    if not isinstance(url, str) or not url or any(ord(c) <= 32 or ord(c) == 127 or c == "\\" for c in url):
        raise ValueError("Invalid model API URL")
    try:
        parsed = urlsplit(url)
        valid = (parsed.scheme in ("http", "https") and parsed.hostname and parsed.port != 0
                 and parsed.username is None and parsed.password is None
                 and "%" not in parsed.hostname and not parsed.fragment)
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("Invalid model API URL")


def _resolve_addresses(host, port):
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses:
        raise ValueError("Failed to resolve model API hostname")
    for family, _, _, _, sockaddr in addresses:
        if family not in (socket.AF_INET, socket.AF_INET6):
            raise ValueError("Unsupported model API address family")
        address = ipaddress.ip_address(sockaddr[0])
        if address.version == 6 and (
            address.ipv4_mapped or address.sixtofour or address.teredo
            or address in _METADATA_NETWORK
            or any(address in network for network in _TRANSLATION_NETWORKS)
        ):
            raise ValueError("Model API address is not allowed")
        # Private model servers are supported; metadata, link-local, multicast,
        # unspecified and other special-purpose addresses are not model endpoints.
        if address.is_multicast or not (
            address.is_global or address.is_loopback or any(address in network for network in _PRIVATE_NETWORKS)
        ):
            raise ValueError("Model API address is not allowed")
    return addresses


class _ProviderConnection:
    def _new_conn(self):
        # Connect to the validated sockaddr directly: no second DNS lookup and
        # no process-wide resolver patch. Keep self.host intact for Host/TLS SNI.
        addresses = _resolve_addresses(self._dns_host, self.port)
        for family, socktype, proto, _, sockaddr in addresses:
            sock = socket.socket(family, socktype, proto)
            try:
                sock.settimeout(self.timeout)
                for option in self.socket_options or ():
                    sock.setsockopt(*option)
                if self.source_address:
                    sock.bind(self.source_address)
                sock.connect(sockaddr)
                return sock
            except BaseException as error:
                sock.close()
                if not isinstance(error, OSError):
                    raise
        raise NewConnectionError(self, "Could not connect to model API")


class _ProviderHTTPConnection(_ProviderConnection, HTTPConnection):
    pass


class _ProviderHTTPSConnection(_ProviderConnection, HTTPSConnection):
    pass


class _ProviderHTTPPool(HTTPConnectionPool):
    ConnectionCls = _ProviderHTTPConnection


class _ProviderHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _ProviderHTTPSConnection


class _ProviderAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        super().init_poolmanager(*args, **kwargs)
        self.poolmanager.pool_classes_by_scheme = {"http": _ProviderHTTPPool, "https": _ProviderHTTPSPool}


def provider_request(method, url, *, timeout=(5, 60), **kwargs):
    """Request a model endpoint without redirects, ambient proxies or error-body disclosure.

    Returns a buffered Response on success. HTTP errors contain only the status;
    neither their body nor their reason phrase is read into a caller-visible error.
    """
    _validate_url(url)
    try:
        with requests.Session() as session:
            session.trust_env = False
            session.mount("http://", _ProviderAdapter())
            session.mount("https://", _ProviderAdapter())
            # requests otherwise consumes a redirect body to build response.next.
            session.resolve_redirects = lambda *args, **kwargs: iter(())
            with session.request(
                method, url, timeout=timeout, allow_redirects=False, stream=True, **kwargs
            ) as response:
                if not 200 <= response.status_code < 300:
                    raise requests.HTTPError(f"Model API request failed: HTTP {response.status_code}")
                response.content
                return response
    except requests.HTTPError:
        raise
    except requests.Timeout:
        raise requests.Timeout("Model API request timed out") from None
    except requests.RequestException:
        raise requests.ConnectionError("Model API connection failed") from None
    except OSError:
        raise requests.ConnectionError("Model API connection failed") from None
