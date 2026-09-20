"""Persist store icons using the same file storage as uploaded tool icons."""

import os
from urllib.parse import urlparse
from uuid import UUID

import requests
import uuid_utils.compat as uuid
from common.exception.app_exception import AppApiException
from common.utils.url_validator import ALLOWED_DOWNLOAD_HOSTS, validate_trusted_url
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from knowledge.models import File, FileSourceType

MAX_ICON_BYTES = 10 * 1024 * 1024


def download_tool_icon(icon, tool_id):
    if not icon:
        return ""
    if not validate_trusted_url(icon, ALLOWED_DOWNLOAD_HOSTS):
        raise AppApiException(500, _("Illegal download url"))
    try:
        with requests.get(icon, timeout=5, allow_redirects=False, stream=True) as response:
            response.raise_for_status()
            # requests does not treat redirects as HTTP errors.
            if response.status_code != 200:
                raise ValueError("Unexpected icon response")
            if not response.headers.get("Content-Type", "").lower().startswith("image/"):
                raise ValueError("Invalid icon content type")
            content = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                content.extend(chunk)
                if len(content) > MAX_ICON_BYTES:
                    raise ValueError("Icon is too large")
            if not content:
                raise ValueError("Empty icon")
    except (requests.RequestException, ValueError) as exc:
        raise AppApiException(500, _("Failed to download tool icon")) from exc

    file_id = uuid.uuid7()
    file = File(
        id=file_id,
        file_name=os.path.basename(urlparse(icon).path)[:256] or "icon",
        source_type=FileSourceType.TOOL,
        source_id=tool_id,
        meta={"debug": False},
    )
    file.save(bytes(content))
    return f"./oss/file/{file_id}"


def delete_tool_icon(icon, tool_id):
    """Delete only local icons owned by this tool, preserving shared template icons."""
    if not icon or not icon.startswith("./oss/file/"):
        return
    try:
        file_id = UUID(icon.removeprefix("./oss/file/"))
    except ValueError:
        return
    QuerySet(File).filter(id=file_id, source_type=FileSourceType.TOOL, source_id=tool_id).delete()
