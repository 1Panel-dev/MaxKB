"""Shared REST/MCP retrieval using the existing vector search and recall statistics."""

import math

from common.config.embedding_config import VectorStore
from knowledge.models import Document, Paragraph, ParagraphAsset, ProblemParagraphMapping, SearchMode, SourceType
from knowledge.serializers.common import get_embedding_model_by_knowledge_id
from knowledge.serializers.external_retrieval import RetrievalRequest
from knowledge.services.retrieval_access import authorize_external, refresh_identity
from knowledge.services.retrieval_stats import record_recall_safely


def valid_source(hit, paragraph):
    source_id, source_type = str(hit.get("source_id")), str(hit.get("source_type"))
    if source_type in {str(SourceType.PARAGRAPH.value), str(SourceType.TITLE.value)}:
        return source_id == str(paragraph.id)
    filters = dict(knowledge_id=paragraph.knowledge_id, document_id=paragraph.document_id, paragraph_id=paragraph.id)
    if source_type == str(SourceType.IMAGE.value):
        return ParagraphAsset.objects.filter(id=source_id, **filters).exists()
    if source_type == str(SourceType.PROBLEM.value):
        return ProblemParagraphMapping.objects.filter(id=source_id, **filters).exists()
    return False


def score(value):
    value = float(value or 0)
    return value if math.isfinite(value) else 0.0


def retrieve(knowledge_id, identity, data):
    request = RetrievalRequest(data=data)
    request.is_valid(raise_exception=True)
    data = request.validated_data
    knowledge = authorize_external(knowledge_id, refresh_identity(identity))
    excluded = list(Document.objects.filter(knowledge_id=knowledge.id, is_active=False).values_list("id", flat=True))
    mode = SearchMode(data["search_mode"])
    model = get_embedding_model_by_knowledge_id(knowledge.id) if mode != SearchMode.keywords else None
    matches = VectorStore.get_embedding_vector().hit_test(
        data["query_text"],
        [str(knowledge.id)],
        list(map(str, excluded)),
        data["top_number"],
        data["similarity"],
        mode,
        model,
    )
    # Check current credentials and publication again after the potentially slow model call.
    knowledge = authorize_external(knowledge_id, refresh_identity(identity))
    paragraphs = {
        str(p.id): p
        for p in Paragraph.objects.select_related("document").filter(
            id__in=[row["paragraph_id"] for row in matches],
            knowledge_id=knowledge.id,
            document__knowledge_id=knowledge.id,
            is_active=True,
            document__is_active=True,
        )
    }
    hits, recalled, seen = [], [], set()
    for match in matches:
        paragraph = paragraphs.get(str(match["paragraph_id"]))
        if paragraph is None or paragraph.id in seen or not valid_source(match, paragraph):
            continue
        seen.add(paragraph.id)
        hits.append(
            {
                "paragraph_id": str(paragraph.id),
                "document_id": str(paragraph.document_id),
                "title": paragraph.title,
                "content": paragraph.content[:8000],
                "similarity": score(match.get("similarity")),
                "comprehensive_score": score(match.get("comprehensive_score")),
                "source_type": match.get("source_type"),
                "source_id": str(match.get("source_id")),
                "citation": {
                    "knowledge_id": str(knowledge.id),
                    "knowledge_name": knowledge.name,
                    "document_id": str(paragraph.document_id),
                    "document_name": paragraph.document.name,
                    "paragraph_id": str(paragraph.id),
                },
            }
        )
        recalled.append(match)
    authorize_external(knowledge_id, refresh_identity(identity))
    record_recall_safely(recalled)
    return {"knowledge_id": str(knowledge.id), "hits": hits}
