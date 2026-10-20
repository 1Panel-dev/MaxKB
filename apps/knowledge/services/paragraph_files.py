"""Keep files and inline assets usable when paragraphs move between documents."""

from collections import defaultdict

import uuid_utils.compat as uuid
from common.exception.app_exception import AppApiException
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from knowledge.models import Document, File, FileSourceType, ParagraphAsset
from knowledge.services import validate_knowledge_file_size


def bind_paragraph_image_files(assets) -> int:
    """Bind inline image files from any importer, preserving source documents and shared IDs."""
    owners = {}
    for asset in assets:
        if not str(asset.source_asset_key).startswith("standalone:"):
            owners.setdefault(str(asset.file_id), asset)
    if not owners:
        return 0
    updated = 0
    with transaction.atomic():
        source_file_ids = {
            str(file_id)
            for file_id in Document.objects.filter(meta__source_file_id__in=list(owners)).values_list(
                "meta__source_file_id", flat=True
            )
        }
        files = (
            File.objects.select_for_update()
            .filter(
                id__in=owners.keys() - source_file_ids,
                source_type__in=[FileSourceType.KNOWLEDGE, FileSourceType.DOCUMENT, FileSourceType.PARAGRAPH],
            )
            .order_by("id")
        )
        for file in files:
            asset = owners[str(file.id)]
            if file.source_type == FileSourceType.KNOWLEDGE and file.source_id != str(asset.knowledge_id):
                continue
            if (
                file.source_type == FileSourceType.DOCUMENT
                and not Document.objects.filter(id=file.source_id, knowledge_id=asset.knowledge_id).exists()
            ):
                continue
            if (
                file.source_type == FileSourceType.PARAGRAPH
                and ParagraphAsset.objects.filter(file_id=file.id, paragraph_id=file.source_id).exists()
            ):
                continue
            # Only a saved, internally consistent asset can transfer file ownership.
            if not ParagraphAsset.objects.filter(
                id=asset.id,
                file_id=file.id,
                paragraph_id=asset.paragraph_id,
                knowledge_id=asset.knowledge_id,
                paragraph__knowledge_id=asset.knowledge_id,
                paragraph__document_id=asset.document_id,
                document__knowledge_id=asset.knowledge_id,
            ).exists():
                continue
            updated += File.objects.filter(id=file.id).update(
                source_type=FileSourceType.PARAGRAPH, source_id=str(asset.paragraph_id)
            )
    return updated


def preserve_incoming_image_files(paragraph_ids, knowledge_id, incoming_paragraphs):
    """Stage reused files before source-authoritative sync deletes their old paragraphs."""
    paragraph_ids = [str(paragraph_id) for paragraph_id in paragraph_ids]
    file_ids = _referenced_file_ids(incoming_paragraphs)
    if paragraph_ids and file_ids:
        image_ids = ParagraphAsset.objects.filter(file_id__in=file_ids, paragraph_id__in=paragraph_ids).values(
            "file_id"
        )
        File.objects.filter(id__in=image_ids, source_type=FileSourceType.PARAGRAPH, source_id__in=paragraph_ids).update(
            source_type=FileSourceType.KNOWLEDGE, source_id=str(knowledge_id)
        )


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
    from knowledge.services.paragraph_assets import FILE_REFERENCE_PATTERN

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
        return owner_id in moving_ids or (
            ParagraphAsset.objects.filter(
                file_id=file.id, paragraph_id=paragraph.id, knowledge_id=paragraph.knowledge_id
            ).exists()
        )
    if file.source_type == FileSourceType.DOCUMENT:
        return owner_id in {str(paragraph.document_id), str(target_document_id)}
    if file.source_type == FileSourceType.KNOWLEDGE:
        return owner_id in {str(paragraph.knowledge_id), str(target_knowledge_id)}
    return False


def detach_shared_paragraph_images(paragraphs, target_knowledge_id):
    """Keep shared images in both knowledge bases when their paragraphs move."""
    paragraphs = [paragraph for paragraph in paragraphs if str(paragraph.knowledge_id) != str(target_knowledge_id)]
    if not paragraphs:
        return
    paragraph_ids = [paragraph.id for paragraph in paragraphs]
    asset_files = ParagraphAsset.objects.filter(paragraph_id__in=paragraph_ids).values("file_id")
    files = (
        File.objects.select_for_update().filter(id__in=asset_files, source_type=FileSourceType.PARAGRAPH).order_by("id")
    )
    for file in files:
        retained_owner = (
            ParagraphAsset.objects.filter(file_id=file.id)
            .exclude(paragraph_id__in=paragraph_ids)
            .order_by("paragraph_id")
            .values_list("paragraph_id", flat=True)
            .first()
        )
        if retained_owner is None:
            continue
        moving_assets = ParagraphAsset.objects.filter(file_id=file.id, paragraph_id__in=paragraph_ids)
        moving_owner = moving_assets.order_by("paragraph_id").values_list("paragraph_id", flat=True).first()
        if moving_owner is None:
            continue
        meta = {**(file.meta or {}), "knowledge_id": str(target_knowledge_id)}
        if file.storage_type == "seaweedfs":
            meta["seaweedfs_key"] = meta.get("seaweedfs_key", f"files/{file.id}")
        copied = File(
            file_name=file.file_name,
            file_size=file.file_size,
            sha256_hash=file.sha256_hash,
            source_type=FileSourceType.PARAGRAPH,
            source_id=str(moving_owner),
            storage_type=file.storage_type,
            loid=file.loid,
            meta=meta,
        )
        # Only the ownership record changes; both files keep referencing the same stored bytes.
        File.objects.bulk_create([copied])
        replacements = {str(file.id): str(copied.id)}
        for paragraph in paragraphs:
            for field in ("content", "content_schema", "source_snapshot", "chunks"):
                setattr(paragraph, field, _replace_file_ids(getattr(paragraph, field), replacements))
            paragraph.save(update_fields=["content", "content_schema", "source_snapshot", "chunks", "update_time"])
        moving_assets.update(file_id=copied.id)
        if file.source_id in {str(paragraph_id) for paragraph_id in paragraph_ids}:
            File.objects.filter(id=file.id).update(source_id=str(retained_owner))


def migrate_paragraph_files(paragraphs, target_document_id, target_knowledge):
    paragraphs = list(paragraphs)
    if not paragraphs:
        return
    detach_shared_paragraph_images(paragraphs, target_knowledge.id)
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
                and (str(file.source_id) in paragraph_ids or str(paragraph.knowledge_id) == str(target_knowledge.id))
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
