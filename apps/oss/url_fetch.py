# coding=utf-8

# Run only in ToolExecutor's dedicated subprocess, never in the web process:
# the resolver is temporarily wrapped for this download. Keep the source here
# so execution does not depend on inspect.getsource in packaged releases.
FETCH_URL_CODE = r'''
def fetch_url(url, file_limit):
    import base64
    import ipaddress
    import socket
    import time
    from urllib.parse import urlsplit

    import requests

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
    if parsed.port == 0:
        raise ValueError("Invalid URL port")

    resolve = socket.getaddrinfo

    def resolve_public(*args, **kwargs):
        addresses = resolve(*args, **kwargs)
        if not addresses:
            raise ValueError("Failed to resolve URL hostname")
        for family, _, _, _, address in addresses:
            if family not in (socket.AF_INET, socket.AF_INET6):
                raise ValueError("Unsupported address family")
            ip = ipaddress.ip_address(address[0])
            if not ip.is_global or ip.is_multicast or ip.is_reserved or (
                ip.version == 6 and (ip.is_site_local or ip.ipv4_mapped or ip.sixtofour or ip.teredo)
            ):
                raise ValueError("Access to non-public IP addresses is blocked")
        return addresses

    # Validate the addresses requests/urllib3 will actually connect to, not a
    # separate DNS lookup followed by an unchecked second resolution.
    deadline = time.monotonic() + 30
    socket.getaddrinfo = resolve_public
    try:
        with requests.Session() as session:
            session.trust_env = False
            # requests otherwise buffers redirect bodies even when redirects are disabled.
            session.resolve_redirects = lambda *args, **kwargs: iter(())
            with session.get(url, stream=True, timeout=(5, 10), allow_redirects=False) as response:
                length = response.headers.get("Content-Length")
                if length is not None:
                    if not length.isascii() or not length.isdecimal():
                        raise ValueError("Invalid Content-Length")
                    if int(length) > file_limit:
                        raise ValueError("File size exceeds limit")
                body = bytearray()
                while True:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("URL download timed out")
                    chunk = response.raw.read1(min(64 * 1024, file_limit - len(body) + 1), decode_content=True)
                    if not chunk:
                        break
                    if len(body) + len(chunk) > file_limit:
                        raise ValueError("File size exceeds limit")
                    body.extend(chunk)
                content_type = response.headers.get("Content-Type", "")
                if "text" in content_type.lower() or "json" in content_type.lower():
                    response._content = bytes(body)
                    content = response.text
                else:
                    content = base64.b64encode(body).decode("ascii")
                return {
                    "status_code": response.status_code,
                    "Content-Type": content_type,
                    "Content-Length": len(body),
                    "content": content,
                }
    finally:
        socket.getaddrinfo = resolve
'''
