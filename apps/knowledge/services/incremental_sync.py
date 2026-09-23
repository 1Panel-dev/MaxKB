"""Stable-ID, three-way paragraph synchronization for external documents."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import uuid_utils.compat as uuid
from common.chunk import text_to_chunk
from django.db import transaction
from django.utils import timezone

from knowledge.models import (
    ContentOrigin,
    Document,
    LocalState,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
    SyncState,
)
from knowledge.services.document_cleanup import delete_synced_paragraph_data
from knowledge.services.document_strategy import (
    document_source_hash,
    normalize_document_strategy,
    stable_hash,
    strategy_hashes,
)


def paragraph_hash(title: str, content: str) -> str:
    return stable_hash({"title": title or "", "content": content or ""})


def _normalized_title(value: str) -> str:
    return " ".join((value or "").strip().lower().split())[:240]


def prepare_remote_paragraphs(paragraphs: Iterable[Dict]) -> List[Dict]:
    """Fill stable keys when a connector cannot provide a native block id."""
    occurrences = defaultdict(int)
    source_key_occurrences = defaultdict(int)
    result = []
    for position, raw in enumerate(paragraphs, 1):
        title, content = raw.get("title") or "", raw.get("content") or ""
        identity = _normalized_title(title) or "untitled"
        occurrences[identity] += 1
        source_key = str(raw.get("source_key") or f"heading:{identity}:{occurrences[identity]}")[:480]
        source_key_occurrences[source_key] += 1
        if source_key_occurrences[source_key] > 1:
            source_key = f"{source_key}:duplicate:{source_key_occurrences[source_key]}"
        result.append(
            {
                **raw,
                "title": title,
                "content": content,
                "position": position,
                "source_key": source_key,
                "source_hash": paragraph_hash(title, content),
            }
        )
    return result


@dataclass
class MergeResult:
    created_ids: List[str] = field(default_factory=list)
    updated_ids: List[str] = field(default_factory=list)
    disabled_ids: List[str] = field(default_factory=list)
    deleted_ids: List[str] = field(default_factory=list)
    conflict_ids: List[str] = field(default_factory=list)
    unchanged_ids: List[str] = field(default_factory=list)

    @property
    def reembed_ids(self) -> List[str]:
        return [*self.created_ids, *self.updated_ids]


class IncrementalDocumentSync:
    def __init__(
        self,
        document: Document,
        strategy: Optional[Dict] = None,
        *,
        source_authoritative: bool = False,
        replace_content: bool = False,
    ):
        self.document = document
        self.strategy = normalize_document_strategy(strategy if strategy is not None else document.doc_strategy)
        # Lark follows source updates/deletes; other connectors retain three-way conflict handling.
        # Neither policy may overwrite manually created paragraphs.
        self.source_authoritative = source_authoritative
        self.replace_content = replace_content

    @staticmethod
    def _snapshot(item: Dict) -> Dict:
        return {"title": item.get("title") or "", "content": item.get("content") or ""}

    def _match(self, remote: Dict, unmatched: List[Paragraph]) -> Optional[Paragraph]:
        unmatched = [p for p in unmatched if p.origin == ContentOrigin.SYNCED]
        if self.source_authoritative:
            by_hash = next(
                (
                    p
                    for p in unmatched
                    if (p.source_hash or paragraph_hash(p.title, p.content)) == remote["source_hash"]
                ),
                None,
            )
            if by_hash is not None:
                return by_hash
            by_title = [p for p in unmatched if _normalized_title(p.title) == _normalized_title(remote["title"])]
            # Repeated headings are paired in source order after unchanged chunks are reserved.
            return next(
                (p for p in by_title if p.source_key == remote["source_key"]), by_title[0] if by_title else None
            )
        exact = next((p for p in unmatched if p.source_key and p.source_key == remote["source_key"]), None)
        if exact:
            return exact
        # Legacy paragraphs have no stable key. Exact content is safe; title/position is only used when unique.
        by_hash = [
            p for p in unmatched if (p.source_hash or paragraph_hash(p.title, p.content)) == remote["source_hash"]
        ]
        if len(by_hash) == 1:
            return by_hash[0]
        by_title = [p for p in unmatched if _normalized_title(p.title) == _normalized_title(remote["title"])]
        if len(by_title) == 1 and abs((by_title[0].position or 0) - remote["position"]) <= 2:
            return by_title[0]
        return None

    def _merge_matched(self, paragraph: Paragraph, remote: Dict, result: MergeResult):
        if self.source_authoritative:
            # An unchanged source chunk must not overwrite a user's local edits.
            if (
                not self.replace_content
                and (paragraph.source_hash or paragraph_hash(paragraph.title, paragraph.content))
                == remote["source_hash"]
                and paragraph.sync_state != SyncState.REMOTE_DELETED
            ):
                updated_fields = []
                if paragraph.source_key != remote["source_key"]:
                    paragraph.source_key = remote["source_key"]
                    updated_fields.append("source_key")
                old_split = normalize_document_strategy(self.document.doc_strategy)["split"]
                if old_split["child_length"] != self.strategy["split"]["child_length"]:
                    paragraph.chunks = text_to_chunk(paragraph.content, self.strategy["split"]["child_length"])
                    updated_fields.append("chunks")
                    result.updated_ids.append(str(paragraph.id))
                else:
                    result.unchanged_ids.append(str(paragraph.id))
                if updated_fields:
                    paragraph.save(update_fields=[*updated_fields, "update_time"])
                return
            paragraph.title, paragraph.content = remote["title"], remote["content"]
            paragraph.chunks = text_to_chunk(paragraph.content, self.strategy["split"]["child_length"])
            paragraph.source_key = remote["source_key"]
            paragraph.source_hash = remote["source_hash"]
            paragraph.source_snapshot = self._snapshot(remote)
            paragraph.source_updated_at = remote.get("source_updated_at")
            paragraph.local_state = LocalState.CLEAN
            paragraph.sync_state = SyncState.ACTIVE
            paragraph.is_active = True
            paragraph.save(
                update_fields=[
                    "title",
                    "content",
                    "chunks",
                    "source_key",
                    "source_hash",
                    "source_snapshot",
                    "source_updated_at",
                    "local_state",
                    "sync_state",
                    "is_active",
                    "update_time",
                ]
            )
            result.updated_ids.append(str(paragraph.id))
            return
        base = paragraph.source_snapshot or {"title": paragraph.title, "content": paragraph.content}
        local = {"title": paragraph.title or "", "content": paragraph.content or ""}
        incoming = self._snapshot(remote)
        local_changed = paragraph.local_state == LocalState.MODIFIED or local != base
        remote_changed = incoming != base

        paragraph.source_key = remote["source_key"]
        paragraph.source_hash = remote["source_hash"]
        paragraph.source_updated_at = remote.get("source_updated_at")
        paragraph.source_snapshot = incoming
        paragraph.origin = ContentOrigin.SYNCED

        if paragraph.local_state == LocalState.DELETED:
            paragraph.sync_state = SyncState.CONFLICT if remote_changed else SyncState.ACTIVE
            paragraph.is_active = False
            (result.conflict_ids if remote_changed else result.unchanged_ids).append(str(paragraph.id))
        elif local_changed and remote_changed and local != incoming:
            paragraph.sync_state = SyncState.CONFLICT
            paragraph.local_state = LocalState.MODIFIED
            paragraph.is_active = True
            result.conflict_ids.append(str(paragraph.id))
        elif not local_changed:
            changed = local != incoming or paragraph.sync_state != SyncState.ACTIVE or not paragraph.is_active
            paragraph.title, paragraph.content = incoming["title"], incoming["content"]
            paragraph.chunks = text_to_chunk(paragraph.content, self.strategy["split"]["child_length"])
            paragraph.local_state = LocalState.CLEAN
            paragraph.sync_state = SyncState.ACTIVE
            paragraph.is_active = True
            (result.updated_ids if changed else result.unchanged_ids).append(str(paragraph.id))
        else:
            # Only local changed (or both arrived at the same value): keep local and advance the base snapshot.
            paragraph.sync_state = SyncState.ACTIVE
            paragraph.is_active = True
            result.unchanged_ids.append(str(paragraph.id))
        paragraph.save(
            update_fields=[
                "title",
                "content",
                "chunks",
                "origin",
                "source_key",
                "source_hash",
                "source_snapshot",
                "source_updated_at",
                "local_state",
                "sync_state",
                "is_active",
                "update_time",
            ]
        )

    def _create(self, remote: Dict, result: MergeResult) -> Paragraph:
        paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            document=self.document,
            knowledge=self.document.knowledge,
            title=remote["title"],
            content=remote["content"],
            chunks=text_to_chunk(remote["content"], self.strategy["split"]["child_length"]),
            position=remote["position"],
            origin=ContentOrigin.SYNCED,
            source_key=remote["source_key"],
            source_hash=remote["source_hash"],
            source_snapshot=self._snapshot(remote),
            source_updated_at=remote.get("source_updated_at"),
            local_state=LocalState.CLEAN,
            sync_state=SyncState.ACTIVE,
        )
        result.created_ids.append(str(paragraph.id))
        return paragraph

    def _handle_remote_deletes(self, unmatched: List[Paragraph], result: MergeResult):
        if self.source_authoritative:
            missing_ids = [p.id for p in unmatched if p.origin == ContentOrigin.SYNCED]
            if missing_ids:
                result.deleted_ids.extend(delete_synced_paragraph_data(self.document.id, missing_ids))
            return
        for paragraph in unmatched:
            if paragraph.origin != ContentOrigin.SYNCED:
                continue
            if paragraph.local_state == LocalState.MODIFIED:
                paragraph.sync_state = SyncState.CONFLICT
                paragraph.is_active = True
                result.conflict_ids.append(str(paragraph.id))
            else:
                paragraph.sync_state = SyncState.REMOTE_DELETED
                paragraph.is_active = False
                result.disabled_ids.append(str(paragraph.id))
            paragraph.save(update_fields=["sync_state", "is_active", "update_time"])

    def _reorder(self, ordered_synced: List[Paragraph], all_existing: List[Paragraph]):
        active_synced = [p for p in ordered_synced if p.sync_state != SyncState.REMOTE_DELETED]
        manual = [p for p in all_existing if p.origin == ContentOrigin.MANUAL and p.local_state != LocalState.DELETED]
        sequence = list(active_synced)
        for item in sorted(manual, key=lambda p: p.position):
            if item.anchor_paragraph_id:
                anchor_index = next((i for i, p in enumerate(sequence) if p.id == item.anchor_paragraph_id), None)
                if anchor_index is not None:
                    sequence.insert(anchor_index + (1 if item.placement == "after" else 0), item)
                    continue
            sequence.append(item)
        for position, paragraph in enumerate(sequence, 1):
            if paragraph.position != position:
                paragraph.position = position
                paragraph.save(update_fields=["position", "update_time"])

    def _sync_title_questions(self, paragraphs: List[Paragraph]):
        auto_mappings = ProblemParagraphMapping.objects.filter(
            document_id=self.document.id, meta__index_source="paragraph_title"
        )
        if self.source_authoritative:
            auto_mappings = auto_mappings.filter(paragraph__origin=ContentOrigin.SYNCED)
        if not self.strategy["index"]["title_as_question"]:
            problem_ids = list(auto_mappings.values_list("problem_id", flat=True))
            auto_mappings.delete()
            Problem.objects.filter(id__in=problem_ids, problemparagraphmapping__isnull=True).delete()
            return
        for paragraph in paragraphs:
            title = (paragraph.title or "").strip()
            stale = auto_mappings.filter(paragraph_id=paragraph.id).exclude(problem__content=title[:256])
            stale_problem_ids = list(stale.values_list("problem_id", flat=True))
            stale.delete()
            Problem.objects.filter(id__in=stale_problem_ids, problemparagraphmapping__isnull=True).delete()
            if not title:
                continue
            problem, _ = Problem.objects.get_or_create(
                knowledge_id=self.document.knowledge_id,
                content=title[:256],
                defaults={"id": uuid.uuid7()},
            )
            mapping, created = ProblemParagraphMapping.objects.get_or_create(
                knowledge_id=self.document.knowledge_id,
                document_id=self.document.id,
                paragraph_id=paragraph.id,
                problem_id=problem.id,
                defaults={"id": uuid.uuid7()},
            )
            if created:
                mapping.meta = {**mapping.meta, "index_source": "paragraph_title"}
                mapping.save(update_fields=["meta", "update_time"])

    @transaction.atomic
    def merge(self, paragraphs: Iterable[Dict]) -> MergeResult:
        remote_list = prepare_remote_paragraphs(paragraphs)
        # Serialize all synchronizations for the same document. Locking only the existing
        # paragraphs does not protect an initially empty document or concurrent inserts.
        self.document = Document.objects.select_for_update().get(id=self.document.id)
        existing = list(Paragraph.objects.select_for_update().filter(document=self.document).order_by("position"))
        if not remote_list and any(
            paragraph.origin == ContentOrigin.SYNCED and paragraph.sync_state != SyncState.REMOTE_DELETED
            for paragraph in existing
        ):
            raise ValueError("Remote synchronization returned an empty paragraph snapshot")
        unmatched = [paragraph for paragraph in existing if paragraph.origin == ContentOrigin.SYNCED]
        ordered_synced, result = [], MergeResult()
        matches = [None] * len(remote_list)
        if self.source_authoritative:
            # Reserve every unchanged chunk before matching changed chunks by title. Otherwise
            # an inserted chunk under a repeated heading could consume an unchanged old chunk.
            for index, remote in enumerate(remote_list):
                paragraph = next(
                    (
                        p
                        for p in unmatched
                        if (p.source_hash or paragraph_hash(p.title, p.content)) == remote["source_hash"]
                    ),
                    None,
                )
                if paragraph is not None:
                    matches[index] = paragraph
                    unmatched.remove(paragraph)
        for index, remote in enumerate(remote_list):
            if matches[index] is None:
                paragraph = self._match(remote, unmatched)
                if paragraph is not None:
                    matches[index] = paragraph
                    unmatched.remove(paragraph)

        if self.source_authoritative:
            self._handle_remote_deletes(unmatched, result)
            # Release changing keys together before a heading reorder swaps unique source keys.
            rekey_ids = [
                paragraph.id
                for remote, paragraph in zip(remote_list, matches)
                if paragraph is not None and paragraph.source_key != remote["source_key"]
            ]
            if rekey_ids:
                Paragraph.objects.filter(document=self.document, id__in=rekey_ids).update(source_key="")
        for remote, paragraph in zip(remote_list, matches):
            if paragraph is None:
                paragraph = self._create(remote, result)
            else:
                self._merge_matched(paragraph, remote, result)
            ordered_synced.append(paragraph)
        if not self.source_authoritative:
            self._handle_remote_deletes(unmatched, result)
        self._reorder(ordered_synced, existing)
        self._sync_title_questions(ordered_synced)

        hashes = strategy_hashes(self.strategy)
        if (
            self.document.split_strategy_hash != hashes["split_strategy_hash"]
            or self.document.visual_strategy_hash != hashes["visual_strategy_hash"]
            or self.document.index_strategy_hash != hashes["index_strategy_hash"]
        ):
            active_paragraphs = Paragraph.objects.filter(document=self.document, is_active=True)
            if self.source_authoritative:
                active_paragraphs = active_paragraphs.filter(origin=ContentOrigin.SYNCED)
            for paragraph_id in active_paragraphs.values_list("id", flat=True):
                value = str(paragraph_id)
                if value not in result.reembed_ids:
                    result.updated_ids.append(value)
        self.document.doc_strategy = self.strategy
        self.document.source_hash = document_source_hash(remote_list)
        self.document.char_length = sum(len(item["content"]) for item in remote_list)
        self.document.sync_version += 1
        self.document.last_sync_time = timezone.now()
        for key, value in hashes.items():
            setattr(self.document, key, value)
        self.document.save(
            update_fields=[
                "doc_strategy",
                "source_hash",
                "char_length",
                "sync_version",
                "last_sync_time",
                "split_strategy_hash",
                "visual_strategy_hash",
                "index_strategy_hash",
                "update_time",
            ]
        )
        return result
