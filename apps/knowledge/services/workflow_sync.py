"""Stable document and paragraph reconciliation for scheduled workflow knowledge runs."""

from collections import defaultdict
from django.db import transaction
from django.db.models import QuerySet

from common.utils.logger import maxkb_logger
from knowledge.models import (
    Document,
    DocumentResourceType,
    DocumentTag,
    Embedding,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeType,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
)
from knowledge.services.incremental_sync import IncrementalDocumentSync, prepare_remote_paragraphs
from knowledge.services.paragraph_assets import process_visual_assets, sync_paragraph_assets
from ops import celery_app


DOCUMENT_IDENTITY_FIELDS = ("source_key", "source_id", "token", "source_url", "url")


def _delete_problems_and_mappings(paragraph_ids) -> None:
    mappings = QuerySet(ProblemParagraphMapping).filter(paragraph_id__in=paragraph_ids)
    problem_ids = set(mappings.values_list("problem_id", flat=True))
    mappings.delete()
    if problem_ids:
        QuerySet(Problem).filter(id__in=problem_ids, problemparagraphmapping__isnull=True).delete()


def _delete_workflow_documents(document_ids) -> list[str]:
    document_ids = [str(document_id) for document_id in document_ids]
    if not document_ids:
        return []
    existing_ids = [
        str(document_id) for document_id in QuerySet(Document).filter(id__in=document_ids).values_list("id", flat=True)
    ]
    if not existing_ids:
        return []
    source_file_ids = [
        source_file_id
        for source_file_id in QuerySet(Document)
        .filter(id__in=existing_ids)
        .values_list("meta__source_file_id", flat=True)
        if source_file_id
    ]
    QuerySet(File).filter(id__in=source_file_ids).delete()
    QuerySet(File).filter(source_type=FileSourceType.DOCUMENT, source_id__in=existing_ids).delete()
    paragraph_ids = list(QuerySet(Paragraph).filter(document_id__in=existing_ids).values_list("id", flat=True))
    _delete_problems_and_mappings(paragraph_ids)
    QuerySet(Embedding).filter(document_id__in=existing_ids).delete()
    QuerySet(Paragraph).filter(id__in=paragraph_ids).delete()
    QuerySet(DocumentTag).filter(document_id__in=existing_ids).delete()
    QuerySet(Document).filter(id__in=existing_ids).delete()
    return existing_ids


def workflow_document_identity(document: Document) -> str:
    meta = document.meta or {}
    for field in DOCUMENT_IDENTITY_FIELDS:
        value = str(meta.get(field) or "").strip()
        if value:
            return f"{field}:{value}"
    return f"name:{' '.join((document.name or '').strip().lower().split())}"


def _copy_document_relations(source: Document, target: Document, source_paragraphs, remote_paragraphs) -> None:
    target_paragraphs = {
        paragraph.source_key: paragraph
        for paragraph in QuerySet(Paragraph).filter(document_id=target.id)
        if paragraph.source_key
    }
    source_key_by_id = {
        str(paragraph.id): remote["source_key"] for paragraph, remote in zip(source_paragraphs, remote_paragraphs)
    }
    for mapping in QuerySet(ProblemParagraphMapping).filter(document_id=source.id):
        target_paragraph = target_paragraphs.get(source_key_by_id.get(str(mapping.paragraph_id), ""))
        if target_paragraph is None:
            continue
        QuerySet(ProblemParagraphMapping).get_or_create(
            knowledge_id=target.knowledge_id,
            document_id=target.id,
            paragraph_id=target_paragraph.id,
            problem_id=mapping.problem_id,
            defaults={"meta": mapping.meta or {}},
        )
    for tag_id in QuerySet(DocumentTag).filter(document_id=source.id).values_list("tag_id", flat=True):
        QuerySet(DocumentTag).get_or_create(document_id=target.id, tag_id=tag_id)
    QuerySet(File).filter(source_type=FileSourceType.DOCUMENT, source_id=str(source.id)).update(
        source_id=str(target.id)
    )


@transaction.atomic
def merge_workflow_incremental_snapshot(sync_log: KnowledgeSyncLog) -> dict:
    """Merge newly generated workflow documents into the previous stable snapshot."""
    new_documents = list(
        QuerySet(Document).filter(
            knowledge_id=sync_log.knowledge_id,
            type=KnowledgeType.WORKFLOW,
            resource_type=DocumentResourceType.DOCUMENT,
            create_time__gte=sync_log.create_time,
        )
    )
    old_documents = list(
        QuerySet(Document).filter(
            knowledge_id=sync_log.knowledge_id,
            type=KnowledgeType.WORKFLOW,
            resource_type=DocumentResourceType.DOCUMENT,
            create_time__lt=sync_log.create_time,
        )
    )
    old_by_identity = defaultdict(list)
    for document in old_documents:
        old_by_identity[workflow_document_identity(document)].append(document)

    matched_old_ids = set()
    synced_count = 0
    skipped_count = 0
    failed_count = 0
    for new_document in new_documents:
        candidates = [
            document
            for document in old_by_identity.get(workflow_document_identity(new_document), [])
            if document.id not in matched_old_ids
        ]
        if not candidates:
            synced_count += 1
            continue
        old_document = candidates[0]
        # Reserve the old identity before merging so a per-document failure can never cause the
        # last good version to be removed as a stale document.
        matched_old_ids.add(old_document.id)
        try:
            source_paragraphs = list(QuerySet(Paragraph).filter(document_id=new_document.id).order_by("position", "id"))
            remote_paragraphs = prepare_remote_paragraphs(
                [
                    {
                        "title": paragraph.title,
                        "content": paragraph.content,
                        "source_key": paragraph.source_key,
                        "source_updated_at": paragraph.source_updated_at,
                    }
                    for paragraph in source_paragraphs
                ]
            )
            result = IncrementalDocumentSync(old_document, new_document.doc_strategy).merge(remote_paragraphs)
            changed_paragraphs = QuerySet(Paragraph).filter(id__in=result.reembed_ids)
            assets = sync_paragraph_assets(changed_paragraphs, old_document.visual_strategy_hash)
            process_visual_assets(assets, old_document.doc_strategy)
            if result.disabled_ids:
                QuerySet(Embedding).filter(paragraph_id__in=result.disabled_ids).delete()

            old_document.name = new_document.name
            old_document.meta = {**(old_document.meta or {}), **(new_document.meta or {})}
            old_document.save(update_fields=["name", "meta", "update_time"])
            _copy_document_relations(new_document, old_document, source_paragraphs, remote_paragraphs)

            # Preserve files transferred to the stable document. The temporary output document
            # must not delete an input/source file now referenced by the stable document.
            new_document.meta = {
                key: value for key, value in (new_document.meta or {}).items() if key != "source_file_id"
            }
            new_document.save(update_fields=["meta", "update_time"])
            _delete_workflow_documents([str(new_document.id)])
            if result.reembed_ids:
                model_id = (
                    QuerySet(Knowledge)
                    .filter(id=old_document.knowledge_id)
                    .values_list("embedding_model_id", flat=True)
                    .first()
                )
                if model_id:
                    transaction.on_commit(
                        lambda paragraph_ids=list(result.reembed_ids), embedding_model_id=str(model_id): (
                            celery_app.send_task(
                                "celery:embedding_by_paragraph_list",
                                args=[paragraph_ids, embedding_model_id],
                            )
                        )
                    )
                synced_count += 1
            else:
                skipped_count += 1
        except Exception:
            maxkb_logger.exception(
                f"Failed to merge workflow document snapshot: knowledge_id={sync_log.knowledge_id}, "
                f"document_id={new_document.id}"
            )
            failed_count += 1

    # A successful workflow run represents a complete output snapshot. Remove old generated
    # documents that were not emitted this time, but never touch standalone image resources.
    deleted_count = 0
    if new_documents and failed_count == 0:
        stale_ids = [str(document.id) for document in old_documents if document.id not in matched_old_ids]
        if stale_ids:
            deleted_count = len(_delete_workflow_documents(stale_ids))
    total_count = (
        QuerySet(Document)
        .filter(
            knowledge_id=sync_log.knowledge_id,
            resource_type=DocumentResourceType.DOCUMENT,
        )
        .count()
    )
    return {
        "total_count": total_count,
        "synced_count": synced_count,
        "skipped_count": skipped_count,
        "deleted_count": deleted_count,
        "failed_count": failed_count,
    }
