"""Persist remote images referenced by Web documents as knowledge assets."""

import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from common.utils.common import get_sha256_hash, guess_image_format
from common.utils.fork import Fork
from common.utils.logger import maxkb_logger
from knowledge.models import File, FileSourceType


REMOTE_IMAGE_PATTERN = re.compile(
    r'!\[(?P<caption>[^\]]*)\]\((?P<url>https?://[^\s)]+)(?:\s+["\'][^"\']*["\'])?\)',
    flags=re.IGNORECASE,
)
MAX_WEB_IMAGE_SIZE = 20 * 1024 * 1024
MAX_WEB_IMAGES_PER_DOCUMENT = 100
IMAGE_EXTENSION = {"jpeg": "jpg", "svg+xml": "svg", "x-icon": "ico"}


def _file_name(source_url: str, image_format: str) -> str:
    path_name = unquote(PurePosixPath(urlsplit(source_url).path).name)
    extension = IMAGE_EXTENSION.get(image_format, image_format)
    if not path_name or "." not in path_name:
        path_name = f"web-image.{extension}"
    return path_name[-256:]


def _cache_web_image(source_url: str, knowledge_id) -> str | None:
    try:
        response = Fork.requests_get(
            source_url,
            {
                "user-agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
                )
            },
        )
        if response.status_code != 200 or not response.content or len(response.content) > MAX_WEB_IMAGE_SIZE:
            return None
        image_format = guess_image_format(response.content, source_url)
        sha256_hash = get_sha256_hash(response.content)
        existing = (
            QuerySet(File)
            .filter(
                source_type=FileSourceType.KNOWLEDGE,
                source_id=str(knowledge_id),
                sha256_hash=sha256_hash,
                meta__source_url=source_url,
            )
            .first()
        )
        if existing is not None:
            return str(existing.id)
        file = File(
            id=uuid.uuid7(),
            file_name=_file_name(source_url, image_format),
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(knowledge_id),
            meta={"knowledge_id": str(knowledge_id), "source_url": source_url},
        )
        file.save(response.content)
        return str(file.id)
    except Exception as exc:
        maxkb_logger.warning(f"Cache web image failed, url={source_url}, error={exc}")
        return None


def internalize_web_images(content: str, knowledge_id) -> str:
    """Replace downloadable remote Markdown images with stable internal file references."""
    cached: dict[str, str | None] = {}

    def replace(match: re.Match) -> str:
        source_url = match.group("url")
        if source_url not in cached:
            cached[source_url] = _cache_web_image(source_url, knowledge_id)
        file_id = cached[source_url]
        if file_id is None:
            return match.group(0)
        return f"![{match.group('caption')}](./oss/file/{file_id})"

    return REMOTE_IMAGE_PATTERN.sub(replace, content or "", count=MAX_WEB_IMAGES_PER_DOCUMENT)
