# coding=utf-8


import traceback
from urllib.parse import urlsplit, urlunsplit

from common.utils.fork import ChildLink, Fork, remove_fragment
from common.utils.logger import maxkb_logger
from django.db.models import QuerySet
from knowledge.models import State, Status, TaskType
from knowledge.models.knowledge import Document, DocumentResourceType, Knowledge, KnowledgeType
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_cleanup import delete_document_data
from knowledge.services.document_strategy import (
    normalize_document_strategy,
    parse_web_content,
    strategy_hashes,
)
from knowledge.web_assets import internalize_web_images


def normalize_web_url(source_url: str) -> str:
    """Return the URL identity used to match crawl results with stored documents."""
    value = remove_fragment((source_url or "").strip())
    parsed = urlsplit(value)
    path = parsed.path.rstrip("/")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, ""))


def _document_name(child_link: ChildLink) -> str:
    tag_text = getattr(child_link.tag, "text", "") if child_link.tag is not None else ""
    return tag_text.strip() if tag_text and tag_text.strip() else child_link.url


def _increment_stats(stats, field, amount=1):
    if stats is not None:
        stats[field] = stats.get(field, 0) + amount


def get_save_handler(knowledge_id, user_id, selector, doc_strategy=None, stats=None):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
    strategy = normalize_document_strategy(
        doc_strategy
        if doc_strategy is not None
        else ((knowledge.meta or {}).get("doc_strategy") if knowledge else None)
    )

    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            try:
                document_name = _document_name(child_link)
                content = internalize_web_images(response.content, knowledge_id)
                paragraphs = parse_web_content(content, strategy)
                DocumentSerializers.Create(data={"knowledge_id": knowledge_id, "user_id": user_id}).save(
                    {
                        "name": document_name,
                        "paragraphs": paragraphs,
                        "meta": {"source_url": child_link.url, "selector": selector},
                        "type": KnowledgeType.WEB,
                        "doc_strategy": strategy,
                    },
                    with_valid=True,
                )
                _increment_stats(stats, "synced_count")
            except Exception as e:
                _increment_stats(stats, "failed_count")
                maxkb_logger.error(f"{str(e)}:{traceback.format_exc()}")
        else:
            _increment_stats(stats, "failed_count")

    return handler


def get_sync_handler(
    knowledge_id,
    user_id,
    doc_strategy=None,
    sync_type="incremental",
    successful_urls=None,
    stats=None,
):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
    if knowledge is None:
        raise ValueError(f"Knowledge does not exist: {knowledge_id}")
    if sync_type not in {"incremental", "replace"}:
        raise ValueError(f"Unsupported Web knowledge synchronization type: {sync_type}")
    strategy = normalize_document_strategy(
        doc_strategy
        if doc_strategy is not None
        else ((knowledge.meta or {}).get("doc_strategy") if knowledge else None)
    )
    document_by_url = {
        normalize_web_url((document.meta or {}).get("source_url", "")): document
        for document in QuerySet(Document).filter(
            knowledge=knowledge,
            type=KnowledgeType.WEB,
            resource_type=DocumentResourceType.DOCUMENT,
        )
        if (document.meta or {}).get("source_url")
    }

    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            source_url = normalize_web_url(child_link.url)
            if successful_urls is not None:
                successful_urls.add(source_url)
            try:
                document_name = _document_name(child_link)
                existing = document_by_url.get(source_url)
                if existing is not None and sync_type == "incremental":
                    # 增量同步使用文档自身策略，并复用本次爬取结果，避免重复请求。
                    previous_sync_version = existing.sync_version
                    DocumentSerializers.Sync(data={"knowledge_id": knowledge.id, "document_id": existing.id}).sync(
                        response=response
                    )
                    if stats is not None:
                        refreshed = QuerySet(Document).filter(id=existing.id).first()
                        sync_state = Status.of(refreshed.status)[TaskType.SYNC] if refreshed is not None else None
                        if sync_state == State.FAILURE:
                            _increment_stats(stats, "failed_count")
                        elif refreshed.sync_version == previous_sync_version:
                            _increment_stats(stats, "skipped_count")
                        else:
                            _increment_stats(stats, "synced_count")
                    return

                selected_strategy = (
                    normalize_document_strategy(existing.doc_strategy) if existing is not None else strategy
                )
                selected_selector = (
                    (existing.meta or {}).get("selector")
                    if existing is not None
                    else (knowledge.meta or {}).get("selector")
                )
                content = internalize_web_images(response.content, knowledge.id)
                paragraphs = parse_web_content(content, selected_strategy)
                created = DocumentSerializers.Create(data={"knowledge_id": knowledge.id, "user_id": user_id}).save(
                    {
                        "name": document_name,
                        "paragraphs": paragraphs,
                        "meta": {"source_url": source_url, "selector": selected_selector},
                        "type": KnowledgeType.WEB,
                        "doc_strategy": selected_strategy,
                    },
                    with_valid=True,
                )
                if existing is not None:
                    # 新文档完整落库后再删除旧文档，避免解析或向量化失败造成数据丢失。
                    delete_document_data([existing.id])
                    _increment_stats(stats, "deleted_count")
                created_id = created.get("id") if isinstance(created, dict) else None
                if created_id:
                    document_by_url[source_url] = QuerySet(Document).filter(id=created_id).first()
                _increment_stats(stats, "synced_count")
            except Exception as e:
                _increment_stats(stats, "failed_count")
                maxkb_logger.error(f"{str(e)}:{traceback.format_exc()}")
        else:
            _increment_stats(stats, "failed_count")

    return handler


def get_sync_web_document_handler(knowledge_id, user_id, doc_strategy=None):
    strategy = normalize_document_strategy(doc_strategy)

    def handler(source_url: str, selector, response: Fork.Response):
        if response.status == 200:
            try:
                content = internalize_web_images(response.content, knowledge_id)
                paragraphs = parse_web_content(content, strategy)
                # 插入
                DocumentSerializers.Create(data={"knowledge_id": knowledge_id, "user_id": user_id}).save(
                    {
                        "name": source_url[0:128],
                        "paragraphs": paragraphs,
                        "meta": {"source_url": source_url, "selector": selector},
                        "type": KnowledgeType.WEB,
                        "doc_strategy": strategy,
                    },
                    with_valid=True,
                )
            except Exception as e:
                maxkb_logger.error(f"{str(e)}:{traceback.format_exc()}")
        else:
            hashes = strategy_hashes(strategy)
            Document(
                name=source_url[0:128],
                knowledge_id=knowledge_id,
                meta={"source_url": source_url, "selector": selector, "allow_download": True},
                type=KnowledgeType.WEB,
                char_length=0,
                status=State.FAILURE,
                user_id=user_id,
                doc_strategy=strategy,
                **hashes,
            ).save()

    return handler
