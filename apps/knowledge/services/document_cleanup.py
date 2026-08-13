"""Shared cleanup operations for document replacement and deletion."""

from collections.abc import Iterable

from django.db import transaction
from django.db.models import QuerySet

from knowledge.models import (
    Document,
    DocumentTag,
    File,
    FileSourceType,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
)
from knowledge.task.embedding import delete_embedding_by_document_list


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
    QuerySet(File).filter(id__in=source_file_ids).delete()
    QuerySet(File).filter(source_id__in=existing_ids, source_type=FileSourceType.DOCUMENT).delete()

    paragraph_ids = list(QuerySet(Paragraph).filter(document_id__in=existing_ids).values_list("id", flat=True))
    _delete_problems_and_mappings(paragraph_ids)
    QuerySet(Paragraph).filter(id__in=paragraph_ids).delete()
    delete_embedding_by_document_list(existing_ids)
    QuerySet(DocumentTag).filter(document_id__in=existing_ids).delete()
    QuerySet(Document).filter(id__in=existing_ids).delete()
    return existing_ids
