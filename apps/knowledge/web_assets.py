"""Persist remote images referenced by Web documents as knowledge assets."""

import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import Q, QuerySet

from common.utils.common import get_sha256_hash, guess_image_format
from common.utils.fork import Fork
from common.utils.logger import maxkb_logger
from knowledge.models import File, FileSourceType, Knowledge, ParagraphAsset


REMOTE_IMAGE_PATTERN = re.compile(
    r'!\[(?P<caption>[^\]]*)\]\((?P<url>https?://[^\s)]+)(?:\s+["\'][^"\']*["\'])?\)',
    flags=re.IGNORECASE,
)
MAX_WEB_IMAGES_PER_DOCUMENT = 100
IMAGE_EXTENSION = {"jpeg": "jpg", "svg+xml": "svg", "x-icon": "ico"}


def _file_name(source_url: str, image_format: str) -> str:
    path_name = unquote(PurePosixPath(urlsplit(source_url).path).name)
    extension = IMAGE_EXTENSION.get(image_format, image_format)
    if not path_name or "." not in path_name:
        path_name = f"web-image.{extension}"
    return path_name[-256:]


def _cached_web_image(source_url, knowledge_id, sha256_hash):
    return (
        QuerySet(File)
        .filter(
            Q(source_type=FileSourceType.KNOWLEDGE, source_id=str(knowledge_id))
            | Q(source_type=FileSourceType.PARAGRAPH, paragraph_assets__knowledge_id=knowledge_id),
            sha256_hash=sha256_hash,
            meta__source_url=source_url,
            storage_type="seaweedfs",
        )
        .first()
    )


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
        if response.status_code != 200 or not response.content:
            return None
        knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
        if knowledge is None or len(response.content) > knowledge.file_size_limit * 1024 * 1024:
            return None
        image_format = guess_image_format(response.content, source_url)
        sha256_hash = get_sha256_hash(response.content)
        existing = _cached_web_image(source_url, knowledge_id, sha256_hash)
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


def bind_web_image_files(assets) -> int:
    """Move staged Web files to a referencing paragraph, retaining shared file IDs."""
    owners = {}
    for asset in assets:
        owners.setdefault(asset.file_id, asset)
    if not owners:
        return 0
    updated = 0
    with transaction.atomic():
        files = (
            File.objects.select_for_update()
            .filter(
                id__in=owners,
                source_type__in=[FileSourceType.KNOWLEDGE, FileSourceType.PARAGRAPH],
                meta__has_key="source_url",
            )
            .order_by("id")
        )
        for file in files:
            asset = owners[file.id]
            if file.source_type == FileSourceType.KNOWLEDGE and file.source_id != str(asset.knowledge_id):
                continue
            if (
                file.source_type == FileSourceType.PARAGRAPH
                and ParagraphAsset.objects.filter(file_id=file.id, paragraph_id=file.source_id).exists()
            ):
                continue
            # Recheck persisted references under the file lock before transferring ownership.
            if not ParagraphAsset.objects.filter(
                id=asset.id,
                file_id=file.id,
                paragraph_id=asset.paragraph_id,
                knowledge_id=asset.knowledge_id,
            ).exists():
                continue
            updated += File.objects.filter(id=file.id).update(
                source_type=FileSourceType.PARAGRAPH, source_id=str(asset.paragraph_id)
            )
    return updated


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
