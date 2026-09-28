"""Keep files and inline assets usable when paragraphs move between documents."""

from collections import defaultdict

import uuid_utils.compat as uuid
from common.exception.app_exception import AppApiException
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from knowledge.models import File, FileSourceType, ParagraphAsset
from knowledge.services import validate_knowledge_file_size
from knowledge.services.paragraph_assets import FILE_REFERENCE_PATTERN


def _replace_file_ids(value, replacements):
    if isinstance(value, str):
        for source_id, target_id in replacements.items():
            value = value.replace(source_id, target_id)
        return value
    if isinstance(value, list):
        return [_replace_file_ids(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_file_ids(item, replacements) for key, item in value.items()}
    return value


def _referenced_file_ids(value):
    if isinstance(value, str):
        return {match.group("file_id") for match in FILE_REFERENCE_PATTERN.finditer(value)}
    if isinstance(value, list):
        return set().union(*(_referenced_file_ids(item) for item in value))
    if isinstance(value, dict):
        result = {str(value["file_id"])} if value.get("file_id") else set()
        return result.union(*(_referenced_file_ids(item) for item in value.values()))
    return set()


def _belongs_to_migrating_paragraph(file, paragraph, moving_ids, target_document_id, target_knowledge_id):
    owner_id = str(file.source_id)
    if file.source_type == FileSourceType.PARAGRAPH:
        return owner_id in moving_ids
    if file.source_type == FileSourceType.DOCUMENT:
        return owner_id in {str(paragraph.document_id), str(target_document_id)}
    if file.source_type == FileSourceType.KNOWLEDGE:
        return owner_id in {str(paragraph.knowledge_id), str(target_knowledge_id)}
    return False


def migrate_paragraph_files(paragraphs, target_document_id, target_knowledge):
    paragraphs = list(paragraphs)
    if not paragraphs:
        return
    paragraph_ids = {str(paragraph.id) for paragraph in paragraphs}
    asset_rows = list(
        ParagraphAsset.objects.filter(paragraph_id__in=paragraph_ids).values("id", "paragraph_id", "file_id")
    )
    assets_by_paragraph = defaultdict(list)
    for asset in asset_rows:
        assets_by_paragraph[str(asset["paragraph_id"])].append(asset)

    referenced_ids = set().union(
        *(
            _referenced_file_ids(
                [paragraph.content, paragraph.content_schema, paragraph.source_snapshot, paragraph.chunks]
            )
            for paragraph in paragraphs
        )
    )
    referenced_ids.update(str(asset["file_id"]) for asset in asset_rows)
    files = list(
        File.objects.filter(
            Q(id__in=referenced_ids) | Q(source_type=FileSourceType.PARAGRAPH, source_id__in=paragraph_ids)
        )
    )
    files_by_id = {str(file.id): file for file in files}
    references_by_paragraph = {}
    for paragraph in paragraphs:
        paragraph_id = str(paragraph.id)
        file_ids = _referenced_file_ids(
            [paragraph.content, paragraph.content_schema, paragraph.source_snapshot, paragraph.chunks]
        )
        file_ids.update(str(asset["file_id"]) for asset in assets_by_paragraph[paragraph_id])
        for file_id in file_ids:
            file = files_by_id.get(file_id)
            if file is not None and not _belongs_to_migrating_paragraph(
                file, paragraph, paragraph_ids, target_document_id, target_knowledge.id
            ):
                raise AppApiException(500, _("File does not belong to the migrated paragraph"))
        references_by_paragraph[paragraph_id] = file_ids
    if any(str(paragraph.knowledge_id) != str(target_knowledge.id) for paragraph in paragraphs):
        validate_knowledge_file_size(target_knowledge, files)

    for paragraph in paragraphs:
        paragraph_id = str(paragraph.id)
        replacements = {}
        for file_id in references_by_paragraph[paragraph_id]:
            file = files_by_id.get(file_id)
            if file is None:
                continue
            if (
                file.source_type == FileSourceType.PARAGRAPH
                and str(file.source_id) in paragraph_ids
                or file.source_type == FileSourceType.DOCUMENT
                and str(file.source_id) == str(target_document_id)
                or file.source_type == FileSourceType.KNOWLEDGE
                and str(file.source_id) == str(target_knowledge.id)
            ):
                continue
            content = file.get_bytes()
            copied = File(
                id=uuid.uuid7(),
                file_name=file.file_name,
                source_type=FileSourceType.PARAGRAPH,
                source_id=paragraph_id,
                meta={
                    **{key: value for key, value in (file.meta or {}).items() if key in {"mime_type", "content_type"}},
                    "original_size": len(content),
                },
            )
            copied.save(content)
            replacements[file_id] = str(copied.id)

        if replacements:
            paragraph.content = _replace_file_ids(paragraph.content, replacements)
            paragraph.content_schema = _replace_file_ids(paragraph.content_schema, replacements)
            paragraph.source_snapshot = _replace_file_ids(paragraph.source_snapshot, replacements)
            paragraph.chunks = _replace_file_ids(paragraph.chunks, replacements)
            paragraph.save(update_fields=["content", "content_schema", "source_snapshot", "chunks", "update_time"])
            for asset in assets_by_paragraph[paragraph_id]:
                replacement = replacements.get(str(asset["file_id"]))
                if replacement:
                    ParagraphAsset.objects.filter(id=asset["id"]).update(file_id=replacement)

    ParagraphAsset.objects.filter(paragraph_id__in=paragraph_ids).update(
        document_id=target_document_id, knowledge_id=target_knowledge.id
    )
