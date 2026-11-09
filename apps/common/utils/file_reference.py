from django.db import transaction
from django.db.models import QuerySet

from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import Document, File, FileSourceType


TEMPORARY_FILE_TYPES = (
    FileSourceType.TEMPORARY_30_MINUTE, FileSourceType.TEMPORARY_120_MINUTE, FileSourceType.TEMPORARY_1_DAY,
)


def validate_owned_upload(file, user_id):
    if (file is None or not user_id or file.source_type not in TEMPORARY_FILE_TYPES
            or str(file.meta.get('user_id')) != str(user_id)):
        raise AppUnauthorizedFailed(403, 'No permission to access')
    return file


def get_owned_upload(file_id, user_id):
    return validate_owned_upload(QuerySet(File).select_for_update().filter(id=file_id).first(), user_id)


def get_knowledge_source_file(file_id, knowledge_id, user_id):
    file = QuerySet(File).filter(id=file_id).first()
    if file is not None and knowledge_id:
        if file.source_type == FileSourceType.KNOWLEDGE and str(file.source_id) == str(knowledge_id):
            return file
        if file.source_type == FileSourceType.DOCUMENT and QuerySet(Document).filter(
            id=file.source_id, knowledge_id=knowledge_id,
        ).exists():
            return file
    return validate_owned_upload(file, user_id)


@transaction.atomic
def bind_knowledge_uploads(file_ids, knowledge_id, user_id):
    files = list(QuerySet(File).select_for_update().filter(id__in=file_ids))
    if {str(file.id) for file in files} != {str(file_id) for file_id in file_ids}:
        raise AppUnauthorizedFailed(403, 'No permission to access')
    for file in files:
        if file.source_type == FileSourceType.KNOWLEDGE and str(file.source_id) == str(knowledge_id):
            continue
        validate_owned_upload(file, user_id)
        file.source_type = FileSourceType.KNOWLEDGE
        file.source_id = str(knowledge_id)
        file.meta = {**file.meta, 'debug': False, 'knowledge_id': str(knowledge_id)}
    QuerySet(File).bulk_update(files, ['source_type', 'source_id', 'meta'])
