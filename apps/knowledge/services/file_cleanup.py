"""Best-effort cleanup of unreferenced S3 objects after database commit."""

from uuid import UUID

from common.storage.seaweedfs import get_s3_client
from common.utils.logger import maxkb_logger
from django.db.models import Q
from knowledge.models import File


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
