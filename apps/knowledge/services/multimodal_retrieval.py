"""Helpers shared by multimodal knowledge retrieval entry points."""

import base64
import mimetypes
from typing import Iterable

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.exception.app_exception import AppApiException
from knowledge.models import File, ParagraphAsset, SourceType


MAX_QUERY_IMAGE_COUNT = 10
MAX_QUERY_IMAGE_SIZE = 20 * 1024 * 1024


def load_image_query_inputs(image_items: Iterable[dict], user_id=None) -> list[str]:
    """Resolve uploaded file references into provider-neutral image data URLs."""
    items = list(image_items or [])
    if not items:
        return []
    if len(items) > MAX_QUERY_IMAGE_COUNT:
        raise AppApiException(
            500,
            _("A maximum of {count} images can be queried at a time").format(count=MAX_QUERY_IMAGE_COUNT),
        )

    file_ids = [str(item.get("file_id")) for item in items]
    files = {str(file.id): file for file in QuerySet(File).filter(id__in=file_ids)}
    image_inputs = []
    for file_id in file_ids:
        file = files.get(file_id)
        if file is None:
            raise AppApiException(500, _("Query image does not exist: {file_id}").format(file_id=file_id))

        owner_id = str((file.meta or {}).get("user_id") or "")
        if owner_id and user_id and owner_id != str(user_id):
            raise AppApiException(403, _("No permission to access the query image"))

        mime_type = mimetypes.guess_type(file.file_name)[0] or ""
        if not mime_type.startswith("image/"):
            raise AppApiException(500, _("Only image files can be used for image queries"))

        content = file.get_bytes()
        if len(content) > MAX_QUERY_IMAGE_SIZE:
            raise AppApiException(
                500,
                _("The maximum size of a query image cannot exceed {size}MB").format(
                    size=MAX_QUERY_IMAGE_SIZE // 1024 // 1024
                ),
            )
        encoded = base64.b64encode(content).decode("ascii")
        image_inputs.append(f"data:{mime_type};base64,{encoded}")
    return image_inputs


def get_hit_asset_map(hit_list: Iterable[dict]) -> dict[str, dict]:
    """Return display metadata for image vectors that won a paragraph hit."""
    asset_ids = {
        str(hit.get("source_id"))
        for hit in hit_list or []
        if str(hit.get("source_type")) == str(SourceType.IMAGE.value) and hit.get("source_id")
    }
    if not asset_ids:
        return {}

    assets = ParagraphAsset.objects.select_related("file").filter(id__in=asset_ids)
    return {
        str(asset.id): {
            "id": str(asset.id),
            "file_id": str(asset.file_id),
            "file_name": asset.file.file_name,
            "url": f"./oss/file/{asset.file_id}",
            "position": asset.position,
            "caption": asset.caption,
            "ocr_text": asset.ocr_text,
            "description": asset.description,
        }
        for asset in assets
    }
