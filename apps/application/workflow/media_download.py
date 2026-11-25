import base64

from oss.url_fetch import fetch_public_url

MAX_GENERATED_IMAGE_BYTES = 20 * 1024 * 1024
MAX_GENERATED_VIDEO_BYTES = 200 * 1024 * 1024


def download_http_bytes(url: str, max_bytes: int) -> bytes:
    response = fetch_public_url(url, max_bytes, binary=True, follow_redirects=True)
    if not 200 <= response["status_code"] < 300:
        raise ValueError(f"Failed to download media: HTTP {response['status_code']}")
    content = base64.b64decode(response["content"], validate=True)
    if not content:
        raise ValueError("HTTP resource is empty")
    return content
