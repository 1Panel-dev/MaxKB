"""Best-effort cleanup of unreferenced S3 objects after database commit."""

from uuid import UUID

from common.storage.seaweedfs import get_s3_client
from common.utils.logger import maxkb_logger
from django.db.models import Q
from knowledge.models import File, FileSourceType, ParagraphAsset


def delete_paragraph_files(paragraph_id, using):
    """Retain shared Web images when their owning paragraph is deleted."""
    files = File.objects.using(using).filter(source_type=FileSourceType.PARAGRAPH, source_id=str(paragraph_id))
    for file in files.select_for_update().filter(meta__has_key="source_url").order_by("id"):
        remaining_owner = (
            ParagraphAsset.objects.using(using)
            .filter(file_id=file.id)
            .exclude(paragraph_id=paragraph_id)
            .order_by("paragraph_id")
            .values_list("paragraph_id", flat=True)
            .first()
        )
        if remaining_owner is not None:
            files.filter(id=file.id).update(source_id=str(remaining_owner))
    files.delete()


def object_is_referenced(key, using):
    references = Q(meta__seaweedfs_key=key)
    if key.startswith("files/"):
        try:
            file_id = UUID(key.removeprefix("files/"))
        except ValueError:
            pass
        else:
            references |= Q(id=file_id) & ~Q(meta__has_key="seaweedfs_key")
    return File.objects.using(using).filter(references, storage_type="seaweedfs").exists()


def delete_file_object(bucket, key, file_id, using="default"):
    try:
        if not object_is_referenced(key, using):
            # S3 deletion is idempotent when a batch contains multiple references to the same key.
            get_s3_client().delete_object(Bucket=bucket, Key=key)
    except Exception as exc:
        # Avoid logging object keys or credentials from SDK error messages.
        maxkb_logger.warning(
            "Failed to clean up OSS object for deleted File %s (%s); manual cleanup may be required",
            file_id,
            type(exc).__name__,
        )
