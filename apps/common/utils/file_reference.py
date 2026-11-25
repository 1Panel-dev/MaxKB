from django.db import transaction
from django.db.models import QuerySet

from common.exception.app_exception import AppUnauthorizedFailed
from common.utils.common import is_valid_uuid
from knowledge.models import Document, File, FileSourceType


TEMPORARY_FILE_TYPES = (
    FileSourceType.TEMPORARY_30_MINUTE, FileSourceType.TEMPORARY_120_MINUTE, FileSourceType.TEMPORARY_1_DAY,
)

CHAT_FILE_FIELDS = ('image_list', 'document_list', 'audio_list', 'video_list', 'other_list',
                    'form_data', 'node_data', 'child_node')


def _iter_file_ids(value):
    if isinstance(value, dict):
        if value.get('file_id'):
            yield str(value.get('file_id'))
        for item in value.values():
            yield from _iter_file_ids(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_file_ids(item)


def validate_file_references(value, is_allowed):
    """校验调用方传入的 file_id 均在允许范围内，防止通过工作流读取他人文件"""
    file_ids = set(_iter_file_ids(value))
    if not file_ids:
        return
    if not all(is_valid_uuid(file_id) for file_id in file_ids):
        raise AppUnauthorizedFailed(403, 'No permission to access')
    files = list(QuerySet(File).filter(id__in=file_ids))
    if len(files) != len(file_ids) or not all(is_allowed(file) for file in files):
        raise AppUnauthorizedFailed(403, 'No permission to access')


def is_owned_upload(file, user_id):
    return (bool(user_id) and file.source_type in (FileSourceType.CHAT, *TEMPORARY_FILE_TYPES)
            and str(file.meta.get('user_id')) == str(user_id))


def validate_chat_file_references(instance, chat_user_id, application_id, chat_id):
    def is_allowed(file):
        if is_owned_upload(file, chat_user_id):
            return True
        return (file.source_type == FileSourceType.APPLICATION and str(file.source_id) == str(application_id)
                and file.meta.get('chat_id') in (None, str(chat_id)))

    validate_file_references([instance.get(key) for key in CHAT_FILE_FIELDS], is_allowed)


def validate_knowledge_file_references(instance, knowledge_id, user_id):
    def is_allowed(file):
        if is_owned_upload(file, user_id):
            return True
        if file.source_type == FileSourceType.KNOWLEDGE:
            return str(file.source_id) == str(knowledge_id)
        if file.source_type == FileSourceType.DOCUMENT:
            return QuerySet(Document).filter(id=file.source_id, knowledge_id=knowledge_id).exists()
        return False

    validate_file_references(instance, is_allowed)


def validate_tool_file_references(instance, tool_id, user_id):
    def is_allowed(file):
        if is_owned_upload(file, user_id):
            return True
        return file.source_type == FileSourceType.TOOL and str(file.source_id) == str(tool_id)

    validate_file_references(instance, is_allowed)


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
