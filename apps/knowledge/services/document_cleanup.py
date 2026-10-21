"""Shared cleanup operations for document replacement and deletion."""

from collections.abc import Iterable

from django.db import transaction
from django.db.models import Q, QuerySet

from knowledge.models import (
    ContentOrigin,
    Document,
    DocumentTag,
    File,
    FileSourceType,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
)
from knowledge.task.embedding import delete_embedding_by_document_list, delete_embedding_by_paragraph_ids


def _delete_problems_and_mappings(paragraph_ids: list[str]) -> None:
    mappings = QuerySet(ProblemParagraphMapping).filter(paragraph_id__in=paragraph_ids)
    problem_ids = set(mappings.values_list("problem_id", flat=True))
    mappings.delete()
    if not problem_ids:
        return
    remaining_problem_ids = set(
        QuerySet(ProblemParagraphMapping).filter(problem_id__in=problem_ids).values_list("problem_id", flat=True)
    )
    QuerySet(Problem).filter(id__in=problem_ids - remaining_problem_ids).delete()


def _delete_document_files(document_ids: list[str], source_file_ids: list[str]) -> None:
    files = list(
        QuerySet(File)
        .filter(Q(id__in=source_file_ids) | Q(source_id__in=document_ids, source_type=FileSourceType.DOCUMENT))
        .select_for_update()
        .order_by("id")
    )
    if not files:
        return
    file_ids = [str(file.id) for file in files]
    remaining_owners = {}
    for file_id, document_id in (
        QuerySet(Document)
        .exclude(id__in=document_ids)
        .filter(meta__source_file_id__in=file_ids)
        .order_by("id")
        .values_list("meta__source_file_id", "id")
    ):
        remaining_owners.setdefault(file_id, (FileSourceType.DOCUMENT, str(document_id)))
    for file_id, paragraph_id in (
        QuerySet(ParagraphAsset)
        .exclude(document_id__in=document_ids)
        .filter(file_id__in=file_ids)
        .order_by("paragraph_id")
        .values_list("file_id", "paragraph_id")
    ):
        remaining_owners.setdefault(str(file_id), (FileSourceType.PARAGRAPH, str(paragraph_id)))

    deleting_ids = []
    for file in files:
        # Legacy metadata can reference a file owned by another document.
        if file.source_type == FileSourceType.DOCUMENT and file.source_id not in document_ids:
            continue
        owner = remaining_owners.get(str(file.id))
        if owner:
            QuerySet(File).filter(id=file.id).update(source_type=owner[0], source_id=owner[1])
        else:
            deleting_ids.append(file.id)
    QuerySet(File).filter(id__in=deleting_ids).delete()


def delete_synced_paragraph_data(document_id, paragraph_ids: Iterable[str]) -> list[str]:
    """Delete missing source paragraphs inside the caller's document-sync transaction.

    Asset rows cascade with paragraphs. Paragraph deletion transfers shared image
    ownership to remaining references; callers stage any incoming image reuse first.
    """
    paragraphs = QuerySet(Paragraph).filter(
        document_id=document_id, id__in=list(paragraph_ids), origin=ContentOrigin.SYNCED
    )
    existing_ids = [str(paragraph_id) for paragraph_id in paragraphs.values_list("id", flat=True)]
    if not existing_ids:
        return []
    _delete_problems_and_mappings(existing_ids)
    delete_embedding_by_paragraph_ids(existing_ids)
    paragraphs.delete()
    return existing_ids


@transaction.atomic
def reset_document_content(document_ids: Iterable[str]) -> list[str]:
    """Remove generated content while retaining document identity and external-source metadata."""
    normalized_ids = [str(document_id) for document_id in document_ids]
    if not normalized_ids:
        return []
    existing_ids = [
        str(document_id)
        for document_id in QuerySet(Document).filter(id__in=normalized_ids).values_list("id", flat=True)
    ]
    if not existing_ids:
        return []
    paragraph_ids = list(QuerySet(Paragraph).filter(document_id__in=existing_ids).values_list("id", flat=True))
    _delete_problems_and_mappings(paragraph_ids)
    QuerySet(Paragraph).filter(id__in=paragraph_ids).delete()
    delete_embedding_by_document_list(existing_ids)
    QuerySet(Document).filter(id__in=existing_ids).update(char_length=0, source_hash="")
    return existing_ids


@transaction.atomic
def delete_document_data(document_ids: Iterable[str]) -> list[str]:
    """Delete documents and every relation managed by the regular document API."""
    normalized_ids = [str(document_id) for document_id in document_ids]
    if not normalized_ids:
        return []

    documents = list(QuerySet(Document).filter(id__in=normalized_ids).values("id", "meta"))
    existing_ids = [str(document["id"]) for document in documents]
    if not existing_ids:
        return []

    source_file_ids = [
        document["meta"].get("source_file_id")
        for document in documents
        if (document.get("meta") or {}).get("source_file_id")
    ]
    paragraph_ids = list(QuerySet(Paragraph).filter(document_id__in=existing_ids).values_list("id", flat=True))
    _delete_problems_and_mappings(paragraph_ids)
    QuerySet(Paragraph).filter(id__in=paragraph_ids).delete()
    _delete_document_files(existing_ids, source_file_ids)
    delete_embedding_by_document_list(existing_ids)
    QuerySet(DocumentTag).filter(document_id__in=existing_ids).delete()
    QuerySet(Document).filter(id__in=existing_ids).delete()
    return existing_ids
