# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： url_validator.py
@date：2025/7/27
@desc: Shared URL validation utilities to prevent SSRF (CWE-918)
"""
from urllib.parse import urlparse

# Allowlist for template/tool/knowledge download asset URLs
ALLOWED_DOWNLOAD_HOSTS = {"apps-assets.fit2cloud.com"}

# Allowlist for download-callback notification URLs
ALLOWED_CALLBACK_HOSTS = {"apps.fit2cloud.com"}


def validate_trusted_url(url, allowed_hosts):
    """Return True only if *url* is a safe HTTPS URL whose hostname is an
    exact (case-insensitive) match against *allowed_hosts*.

    Rejects:
    - Non-string or empty values.
    - Non-HTTPS schemes.
    - URLs containing userinfo (user:pass@host).
    - URLs with an explicit port number.
    - Hostnames not present in *allowed_hosts*.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
    except (ValueError, TypeError):
        return False
    if parsed.scheme != "https":
        return False
    if parsed.username or parsed.password:
        return False
    if parsed.port is not None:
        return False
    hostname = (parsed.hostname or "").lower()
    return hostname in allowed_hosts
