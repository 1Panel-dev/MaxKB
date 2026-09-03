import threading
from contextlib import nullcontext
from typing import Iterable

from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone

from common.utils.logger import maxkb_logger
from knowledge.models import Document, Paragraph, ParagraphAsset, Problem, ProblemParagraphMapping, SourceType


def _value(item, key):
    return item.get(key) if isinstance(item, dict) else getattr(item, key, None)


def collect_recall_source_ids(recall_items: Iterable) -> tuple[set[str], set[str]]:
    """收集本次召回中的分段和问题映射 ID。

    向量查询会对每个分段保留得分最高的可检索单元；只有该单元来自问题时，
    才将对应问题计为本次召回。
    """
    paragraph_ids = set()
    problem_mapping_ids = set()
    for item in recall_items or []:
        paragraph_id = _value(item, "paragraph_id")
        if paragraph_id is not None:
            paragraph_ids.add(str(paragraph_id))
        if str(_value(item, "source_type")) == str(SourceType.PROBLEM.value):
            source_id = _value(item, "source_id")
            if source_id is not None:
                problem_mapping_ids.add(str(source_id))
    return paragraph_ids, problem_mapping_ids


def collect_recall_asset_ids(recall_items: Iterable) -> set[str]:
    """收集最终命中图片检索单元对应的资产 ID。"""
    return {
        str(source_id)
        for item in recall_items or []
        if str(_value(item, "source_type")) == str(SourceType.IMAGE.value)
        and (source_id := _value(item, "source_id")) is not None
    }


def _only_new_ids(tracker: dict | None, key: str, ids: set[str]) -> set[str]:
    if tracker is None:
        return ids
    seen_ids = tracker.setdefault(key, set())
    new_ids = ids - seen_ids
    seen_ids.update(ids)
    return new_ids


def get_recall_tracker(owner) -> dict:
    tracker = getattr(owner, "_knowledge_recall_tracker", None)
    if tracker is None:
        tracker = {}
        setattr(owner, "_knowledge_recall_tracker", tracker)
    return tracker


def record_recall(recall_items: Iterable, tracker: dict | None = None, recalled_at=None) -> None:
    recall_items = list(recall_items or [])
    paragraph_ids, problem_mapping_ids = collect_recall_source_ids(recall_items)
    asset_ids = collect_recall_asset_ids(recall_items)
    if not paragraph_ids:
        return

    paragraph_document_pairs = QuerySet(Paragraph).filter(id__in=paragraph_ids).values_list("id", "document_id")
    existing_paragraph_ids = {str(paragraph_id) for paragraph_id, _ in paragraph_document_pairs}
    recalled_paragraph_ids = existing_paragraph_ids
    document_ids = {str(document_id) for _, document_id in paragraph_document_pairs}

    problem_ids = set()
    if problem_mapping_ids:
        problem_ids = {
            str(problem_id)
            for problem_id in QuerySet(ProblemParagraphMapping)
            .filter(id__in=problem_mapping_ids, paragraph_id__in=existing_paragraph_ids)
            .values_list("problem_id", flat=True)
        }

    tracker_lock = tracker.setdefault("_lock", threading.Lock()) if tracker is not None else nullcontext()
    with tracker_lock:
        existing_paragraph_ids = _only_new_ids(tracker, "paragraph_ids", existing_paragraph_ids)
        document_ids = _only_new_ids(tracker, "document_ids", document_ids)
        problem_ids = _only_new_ids(tracker, "problem_ids", problem_ids)
        asset_ids = _only_new_ids(tracker, "asset_ids", asset_ids)
    recalled_at = recalled_at or timezone.now()

    with transaction.atomic():
        if existing_paragraph_ids:
            QuerySet(Paragraph).filter(id__in=existing_paragraph_ids).update(
                hit_num=F("hit_num") + 1, last_hit_time=recalled_at
            )
        if document_ids:
            QuerySet(Document).filter(id__in=document_ids).update(hit_num=F("hit_num") + 1, last_hit_time=recalled_at)
        if problem_ids:
            QuerySet(Problem).filter(id__in=problem_ids).update(hit_num=F("hit_num") + 1, last_hit_time=recalled_at)
        if asset_ids:
            QuerySet(ParagraphAsset).filter(
                id__in=asset_ids,
                paragraph_id__in=recalled_paragraph_ids,
            ).update(hit_num=F("hit_num") + 1, last_hit_time=recalled_at)


def record_recall_safely(recall_items: Iterable, tracker: dict | None = None) -> None:
    try:
        record_recall(recall_items, tracker=tracker)
    except Exception:
        # 统计失败不应中断用户的检索和对话。
        maxkb_logger.exception("Failed to update knowledge recall statistics")
