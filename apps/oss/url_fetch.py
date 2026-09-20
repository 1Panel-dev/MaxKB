# coding=utf-8


def fetch_public_url(url, file_limit):
    """Download a public HTTP(S) URL inside ToolExecutor's sandbox.

    Keep this function self-contained: its source is sent to the sandbox, which
    cannot import application modules. Resolve once and connect to the checked
    socket addresses, while preserving the hostname for HTTP and TLS.
    """
    import base64
    import ipaddress
    import socket
    import time
    from urllib.parse import urlsplit

    import requests
    from urllib3 import HTTPConnectionPool, HTTPSConnectionPool
    from urllib3.connection import HTTPConnection, HTTPSConnection
    from urllib3.exceptions import NewConnectionError
    from urllib3.util import Timeout

    file_limit = int(file_limit)
    if file_limit <= 0:
        raise ValueError("Invalid file size limit")
    if not isinstance(url, str) or not url or any(ord(c) <= 32 or ord(c) == 127 or c == "\\" for c in url):
        raise ValueError("Invalid URL")
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    if parsed.username is not None or parsed.password is not None or "%" in parsed.hostname:
        raise ValueError("URL credentials and scoped or encoded hostnames are not allowed")
    if parsed.port is not None and parsed.port == 0:
        raise ValueError("Invalid URL port")

    # Use the HTTP client's normalized hostname (including IDNA), not a second
    # parser's interpretation of the original URL.
    prepared = requests.Request("GET", url).prepare()
    parsed = urlsplit(prepared.url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    addresses = socket.getaddrinfo(parsed.hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    if not addresses:
        raise ValueError("Failed to resolve URL hostname")
    for family, _, _, _, address in addresses:
        if family not in (socket.AF_INET, socket.AF_INET6):
            raise ValueError("Unsupported address family")
        ip = ipaddress.ip_address(address[0])
        if not ip.is_global or ip.is_multicast or ip.is_reserved:
            raise ValueError("Access to non-public IP addresses is blocked")
        if isinstance(ip, ipaddress.IPv6Address) and (
            ip.ipv4_mapped is not None
            or ip.sixtofour is not None
            or ip.teredo is not None
            or ip in ipaddress.ip_network("64:ff9b::/96")
            or ip in ipaddress.ip_network("64:ff9b:1::/48")
        ):
            raise ValueError("Access to IPv6 transition addresses is blocked")

    deadline = time.monotonic() + 30

    class PinnedConnection:
        def _new_conn(self):
            last_error = None
            for family, socktype, proto, _, address in addresses:
                if time.monotonic() >= deadline:
                    raise TimeoutError("URL download timed out")
                sock = socket.socket(family, socktype, proto)
                try:
                    sock.settimeout(min(self.timeout, max(0.001, deadline - time.monotonic())))
                    for option in self.socket_options or ():
                        sock.setsockopt(*option)
                    # Do not pass the hostname to create_connection/getaddrinfo
                    # again: DNS may have changed since validation.
                    sock.connect(address)
                    return sock
                except OSError as exc:
                    last_error = exc
                    sock.close()
            raise NewConnectionError(self, "Could not connect to URL") from last_error

    class PinnedHTTPConnection(PinnedConnection, HTTPConnection):
        pass

    class PinnedHTTPSConnection(PinnedConnection, HTTPSConnection):
        pass

    if parsed.scheme == "https":
        pool = HTTPSConnectionPool(parsed.hostname, port, cert_reqs="CERT_REQUIRED", ca_certs=requests.certs.where())
        pool.ConnectionCls = PinnedHTTPSConnection
    else:
        pool = HTTPConnectionPool(parsed.hostname, port)
        pool.ConnectionCls = PinnedHTTPConnection

    response = None
    try:
        # Direct pools do not inherit HTTP_PROXY/HTTPS_PROXY or .netrc credentials.
        response = pool.urlopen(
            "GET",
            prepared.path_url,
            headers={"Host": parsed.netloc, "Accept-Encoding": "identity"},
            redirect=False,
            retries=False,
            preload_content=False,
            timeout=Timeout(connect=5, read=10),
        )
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            if not content_length.isascii() or not content_length.isdecimal():
                raise ValueError("Invalid Content-Length")
            if int(content_length) > file_limit:
                raise ValueError("File size exceeds limit")

        # Count decoded bytes as they arrive, including chunked/compressed bodies
        # and responses without Content-Length. Never trust a header as the limit.
        body = bytearray()
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("URL download timed out")
            chunk = response.read1(min(64 * 1024, file_limit - len(body) + 1), decode_content=True)
            if not chunk:
                break
            if len(body) + len(chunk) > file_limit:
                raise ValueError("File size exceeds limit")
            body.extend(chunk)

        content_type = response.headers.get("Content-Type", "")
        if "text" in content_type.lower() or "json" in content_type.lower():
            # Preserve requests' charset detection and text/binary response format.
            decoded = requests.Response()
            decoded._content = bytes(body)
            decoded.encoding = requests.utils.get_encoding_from_headers(response.headers)
            content = decoded.text
        else:
            content = base64.b64encode(body).decode("ascii")
        return {
            "status_code": response.status,
            "Content-Type": content_type,
            "Content-Length": len(body),
            "content": content,
        }
    finally:
        if response is not None:
            response.close()
        pool.close()
