from urllib.parse import urlparse

import requests

HTTP_DOWNLOAD_TIMEOUT = (5, 30)
HTTP_DOWNLOAD_CHUNK_SIZE = 64 * 1024
MAX_GENERATED_IMAGE_BYTES = 20 * 1024 * 1024
MAX_GENERATED_VIDEO_BYTES = 200 * 1024 * 1024


def download_http_bytes(url: str, max_bytes: int) -> bytes:
    if max_bytes <= 0:
        raise ValueError("Download size limit must be positive")

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("Only HTTP resources can be downloaded")

    with requests.get(url, stream=True, timeout=HTTP_DOWNLOAD_TIMEOUT) as response:
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except (TypeError, ValueError):
                declared_size = None
            if declared_size is not None and declared_size > max_bytes:
                raise ValueError("HTTP resource is too large")

        content = bytearray()
        for chunk in response.iter_content(chunk_size=HTTP_DOWNLOAD_CHUNK_SIZE):
            if not chunk:
                continue
            if len(content) + len(chunk) > max_bytes:
                raise ValueError("HTTP resource is too large")
            content.extend(chunk)

    if not content:
        raise ValueError("HTTP resource is empty")
    return bytes(content)
