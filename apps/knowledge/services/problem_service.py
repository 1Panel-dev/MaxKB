"""Problem association services shared by generation tasks."""

import re

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.utils.logger import maxkb_logger
from knowledge.models import Knowledge, Paragraph, Problem, ProblemParagraphMapping, SourceType
from knowledge.task.embedding import embedding_by_problem


@transaction.atomic
def save_problem(knowledge_id, document_id, paragraph_id, generated_text) -> None:
    """Persist one generated question and build its embedding."""
    generated_text = re.sub(r"^\d+\.\s*", "", generated_text)
    match = re.search(r"<question>(.*?)</question>", generated_text, flags=re.DOTALL)
    content = match.group(1) if match else None
    if not content:
        return

    try:
        paragraph_exists = (
            QuerySet(Paragraph)
            .filter(
                id=paragraph_id,
                document_id=document_id,
                knowledge_id=knowledge_id,
            )
            .exists()
        )
        if not paragraph_exists:
            return

        problem = QuerySet(Problem).filter(knowledge_id=knowledge_id, content=content).first()
        if problem is None:
            problem = Problem(id=uuid.uuid7(), knowledge_id=knowledge_id, content=content)
            problem.save()

        mapping = (
            QuerySet(ProblemParagraphMapping)
            .filter(
                knowledge_id=knowledge_id,
                problem_id=problem.id,
                paragraph_id=paragraph_id,
            )
            .first()
        )
        if mapping is not None:
            return

        mapping = ProblemParagraphMapping(
            id=uuid.uuid7(),
            problem_id=problem.id,
            document_id=document_id,
            paragraph_id=paragraph_id,
            knowledge_id=knowledge_id,
        )
        mapping.save()
        knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
        if knowledge is None or knowledge.embedding_model_id is None:
            return
        embedding_by_problem(
            {
                "text": problem.content,
                "is_active": True,
                "source_type": SourceType.PROBLEM,
                "source_id": mapping.id,
                "document_id": document_id,
                "paragraph_id": paragraph_id,
                "knowledge_id": knowledge_id,
            },
            str(knowledge.embedding_model_id),
        )
    except Exception as exc:
        maxkb_logger.error(_("Association problem failed {error}").format(error=str(exc)))
