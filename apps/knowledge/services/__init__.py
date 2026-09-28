"""Knowledge domain services."""

from common.exception.app_exception import AppApiException
from django.utils.translation import gettext_lazy as _


def validate_knowledge_file_size(knowledge, files):
    for file in files:
        size = getattr(file, "size", None)
        if size is None:
            # PostgreSQL stores compressed bytes, while the limit applies to the uploaded file.
            size = (getattr(file, "meta", None) or {}).get("original_size", file.file_size)
        if size > 1024 * 1024 * knowledge.file_size_limit:
            raise AppApiException(
                500,
                _("The maximum size of the uploaded file cannot exceed {}MB").format(knowledge.file_size_limit),
            )
