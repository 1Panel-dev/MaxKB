# coding=utf-8
"""
@project: maxkb
@file： milvus_vector.py
@desc: Milvus 向量库实现（REST API 接入，不依赖 pymilvus SDK）。混合存储：
       向量存 Milvus，元数据 + tsvector 全文存 PG。每个知识库一个 collection
       （maxkb_kb_{knowledge_id}），HNSW + COSINE。
       PG 的 Embedding 表为元数据 source of truth，Milvus 按 Embedding.id 镜像向量。
       连接通过 MILVUS_URI + MILVUS_TOKEN（Authorization: Bearer {token}）。
"""

from collections import defaultdict
from functools import partial
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from common.exception.app_exception import AppApiException
from common.utils.logger import maxkb_logger
from common.utils.ts_vecto_util import to_ts_vector
from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import F, QuerySet, Value
from django.utils.translation import gettext_lazy as _
from knowledge.models import Embedding, LocalState, SearchMode, Termbase
from knowledge.vector.base_vector import BaseVectorStore, normalize_for_embedding
from knowledge.vector.pg_fulltext import text_rank_by_ids, pg_vector_recall
from knowledge.vector.pg_vector import KeywordsSearch
from models_provider.base_model_provider import MaxKBBaseEmbeddingModel

# Milvus REST API v2 路径
_PATH_HAS = "/v2/vectordb/collections/has"
_PATH_CREATE = "/v2/vectordb/collections/create"
_PATH_DROP = "/v2/vectordb/collections/drop"
_PATH_LOAD = "/v2/vectordb/collections/load"
_PATH_UPSERT = "/v2/vectordb/entities/upsert"
_PATH_DELETE = "/v2/vectordb/entities/delete"
_PATH_SEARCH = "/v2/vectordb/entities/search"
_PATH_QUERY = "/v2/vectordb/entities/query"


class MilvusVector(BaseVectorStore):
    _session = None
    _uri = ""
    _existing = set()  # 已确认存在的 collection 缓存（drop 时失效）
    _loaded = set()  # 本进程确认加载成功后才允许跳过写入前准备

    # ------------------------------------------------------------------ #
    # HTTP 封装
    # ------------------------------------------------------------------ #
    @classmethod
    def _get_session(cls):
        if cls._session is None:
            from maxkb.const import CONFIG

            # MILVUS_URI 为空时回退本机（仅显式选 milvus 但未配 URI 时触发）
            cls._uri = (CONFIG.get("MILVUS_URI") or "http://127.0.0.1:19530").rstrip("/")
            token = CONFIG.get("MILVUS_TOKEN", "") or ""
            s = requests.Session()
            s.headers.update({"Content-Type": "application/json"})
            if token:
                s.headers.update({"Authorization": f"Bearer {token}"})
            cls._session = s
        return cls._session

    @classmethod
    def _post(cls, path: str, body: dict):
        """调用 Milvus REST，仅 HTTP 2xx 且业务 code 为整数 0 时成功。"""
        s = cls._get_session()
        url = f"{cls._uri}{path}"
        try:
            resp = s.post(url, json=body, timeout=120)
        except requests.RequestException as e:
            maxkb_logger.error(f"Milvus REST {path} request error: {e}")
            return False, {"code": -1, "message": str(e)}
        try:
            data = resp.json()
        except ValueError:
            maxkb_logger.error(f"Milvus REST {path} bad response: {resp.status_code} {resp.text[:200]}")
            return False, {"code": -1, "message": f"HTTP {resp.status_code}: invalid JSON response"}
        if not 200 <= resp.status_code < 300:
            message = data.get("message", resp.reason) if isinstance(data, dict) else resp.reason
            return False, {"code": resp.status_code, "message": f"HTTP {resp.status_code}: {message}"}
        if not isinstance(data, dict) or type(data.get("code")) is not int:
            return False, {"code": -1, "message": "Invalid Milvus response: expected an integer code"}
        if data["code"] != 0:
            return False, data
        return True, data

    @classmethod
    def _post_required(cls, path: str, body: dict):
        """写入依赖的请求必须成功，异常交由调用方更新向量化失败状态。"""
        ok, data = cls._post(path, body)
        if not ok:
            # A different worker can drop a collection behind either process-local cache.
            for knowledge_id in cls._existing | cls._loaded:
                if cls._collection_name(knowledge_id) == body.get("collectionName"):
                    cls._existing.discard(knowledge_id)
                    cls._loaded.discard(knowledge_id)
            message = (
                f"Milvus request failed ({path}, collection={body.get('collectionName')}, "
                f"code={data.get('code')}): {data.get('message', 'Unknown error')}"
            )
            maxkb_logger.error(message)
            raise AppApiException(500, message)
        return data

    @staticmethod
    def _collection_name(knowledge_id: str) -> str:
        # Milvus collection 名仅允许字母/数字/下划线，uuid 含 '-' 需替换
        return f"maxkb_kb_{str(knowledge_id).replace('-', '_')}"

    def _has_collection(self, knowledge_id: str, *, raise_on_error=False) -> bool:
        knowledge_id = str(knowledge_id)
        if knowledge_id in MilvusVector._existing:
            return True
        body = {"collectionName": self._collection_name(knowledge_id)}
        if raise_on_error:
            data = self._post_required(_PATH_HAS, body)
            ok = True
        else:
            ok, data = self._post(_PATH_HAS, body)
        payload = data.get("data") if ok else None
        if not isinstance(payload, dict) or not isinstance(payload.get("has"), bool):
            if raise_on_error:
                raise AppApiException(500, f"Invalid Milvus response ({_PATH_HAS}): expected boolean data.has")
            return False
        if payload["has"]:
            MilvusVector._existing.add(knowledge_id)
            return True
        return False

    def _ensure_collection(self, knowledge_id: str, dim: int):
        knowledge_id = str(knowledge_id)
        if not dim or dim <= 0:
            raise AppApiException(500, _("Invalid Milvus vector dimension"))
        if knowledge_id in MilvusVector._loaded:
            return
        exists = self._has_collection(knowledge_id, raise_on_error=True)
        name = self._collection_name(knowledge_id)
        body = {
            "collectionName": name,
            "schema": {
                "autoID": False,
                "enableDynamicField": False,
                "fields": [
                    {
                        "fieldName": "id",
                        "dataType": "VarChar",
                        "isPrimary": True,
                        "elementTypeParams": {"max_length": 128},
                    },
                    {"fieldName": "embedding", "dataType": "FloatVector", "elementTypeParams": {"dim": dim}},
                    {"fieldName": "document_id", "dataType": "VarChar", "elementTypeParams": {"max_length": 128}},
                    {"fieldName": "paragraph_id", "dataType": "VarChar", "elementTypeParams": {"max_length": 128}},
                    {"fieldName": "is_active", "dataType": "Bool"},
                    {"fieldName": "source_id", "dataType": "VarChar", "elementTypeParams": {"max_length": 128}},
                    {"fieldName": "source_type", "dataType": "Int8"},
                ],
            },
            "indexParams": [
                {
                    "fieldName": "embedding",
                    "indexType": "HNSW",
                    "metricType": "COSINE",
                    "params": {"M": 16, "efConstruction": 256},
                }
            ],
        }
        if not exists:
            self._post_required(_PATH_CREATE, body)
        # 也加载已存在的 collection，允许上次创建成功但加载失败后重新尝试。
        self._post_required(_PATH_LOAD, {"collectionName": name})
        MilvusVector._existing.add(knowledge_id)
        MilvusVector._loaded.add(knowledge_id)
        maxkb_logger.info(f"Prepared Milvus collection for knowledge ID: {knowledge_id} (dim={dim})")

    def vector_is_create(self) -> bool:
        # collection 按需懒创建，无需全局初始化
        return True

    def vector_create(self):
        return True

    def ensure_knowledge_index(self, knowledge_id: str, dim: int = None):
        # 文档向量化时 collection 已在 _batch_save 懒创建；此处仅按给定 dim 幂等创建
        if dim is not None:
            self._ensure_collection(knowledge_id, dim)

    def drop_knowledge_index(self, knowledge_id: str):
        knowledge_id = str(knowledge_id)
        if not self._has_collection(knowledge_id):
            return
        ok, data = self._post(_PATH_DROP, {"collectionName": self._collection_name(knowledge_id)})
        if ok:
            MilvusVector._existing.discard(knowledge_id)
            MilvusVector._loaded.discard(knowledge_id)
            maxkb_logger.info(f"Dropped Milvus collection for knowledge ID: {knowledge_id}")
        else:
            maxkb_logger.error(f"Drop Milvus collection failed (kid={knowledge_id}): {data}")

    # ------------------------------------------------------------------ #
    # 写入
    # ------------------------------------------------------------------ #
    def _save(
        self,
        text,
        source_type,
        knowledge_id: str,
        document_id: str,
        paragraph_id: str,
        source_id: str,
        is_active: bool,
        embedding: MaxKBBaseEmbeddingModel,
    ):
        self._batch_save(
            [
                {
                    "text": text,
                    "source_type": source_type,
                    "knowledge_id": knowledge_id,
                    "document_id": document_id,
                    "paragraph_id": paragraph_id,
                    "source_id": source_id,
                    "is_active": is_active,
                }
            ],
            embedding,
            lambda: False,
        )

    def _batch_save(self, text_list: List[Dict], embedding: MaxKBBaseEmbeddingModel, is_the_task_interrupted):
        if not text_list:
            return True
        texts = [normalize_for_embedding(row.get("text")) for row in text_list]
        vectors = embedding.embed_documents(texts)
        kid = text_list[0].get("knowledge_id")
        dim = len(vectors[0]) if vectors else 0
        self._ensure_collection(kid, dim)
        terms = list(QuerySet(Termbase).filter(knowledge_id=kid).values_list("content", flat=True))
        embedding_objs = []
        records = []
        for index, row in enumerate(text_list):
            eid = str(uuid.uuid7())
            # PG 元数据 + tsvector（不写 embedding 向量列，向量交由 Milvus）
            embedding_objs.append(
                Embedding(
                    id=eid,
                    document_id=row.get("document_id"),
                    paragraph_id=row.get("paragraph_id"),
                    knowledge_id=row.get("knowledge_id"),
                    is_active=row.get("is_active", True),
                    source_id=row.get("source_id"),
                    source_type=row.get("source_type"),
                    search_vector=SearchVector(Value(to_ts_vector(texts[index], user_words=terms)), config="simple"),
                )
            )
            records.append(
                {
                    "id": eid,
                    "embedding": [float(x) for x in vectors[index]],
                    "document_id": str(row.get("document_id") or ""),
                    "paragraph_id": str(row.get("paragraph_id") or ""),
                    "is_active": bool(row.get("is_active", True)),
                    "source_id": str(row.get("source_id") or ""),
                    "source_type": int(row.get("source_type")),
                }
            )
        if not is_the_task_interrupted():
            QuerySet(Embedding).bulk_create(embedding_objs) if embedding_objs else None
            self._upsert_records(kid, records)
        return True

    def _upsert_records(self, knowledge_id: str, records: List[Dict]):
        if not records:
            return
        dim = len(records[0]["embedding"])
        self._ensure_collection(knowledge_id, dim)
        name = self._collection_name(knowledge_id)
        for i in range(0, len(records), 500):
            self._post_required(_PATH_UPSERT, {"collectionName": name, "data": records[i : i + 500]})

    # ------------------------------------------------------------------ #
    # 删除
    # ------------------------------------------------------------------ #
    def _delete_ids(self, knowledge_id: str, ids: List[str]):
        if not ids or not self._has_collection(knowledge_id, raise_on_error=True):
            return
        name = self._collection_name(knowledge_id)
        for i in range(0, len(ids), 1000):
            batch = ids[i : i + 1000]
            self._post_required(_PATH_DELETE, {"collectionName": name, "filter": f"id in {self._str_list(batch)}"})

    def _delete_by_filter(self, filter_kwargs: Dict):
        matched = list(QuerySet(Embedding).filter(**filter_kwargs).values("id", "knowledge_id"))
        if matched:
            by_kid = defaultdict(list)
            for r in matched:
                by_kid[str(r["knowledge_id"])].append(str(r["id"]))
            for kid, ids in by_kid.items():
                self._delete_ids(kid, ids)
        QuerySet(Embedding).filter(**filter_kwargs).delete()

    def delete_by_knowledge_id(self, knowledge_id: str):
        # 整库向量集中在单一 collection，直接 drop
        self.drop_knowledge_index(knowledge_id)
        QuerySet(Embedding).filter(knowledge_id=knowledge_id).delete()

    def delete_by_knowledge_id_list(self, knowledge_id_list: List[str]):
        for kid in knowledge_id_list:
            self.drop_knowledge_index(kid)
        QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list).delete()

    def delete_by_document_id(self, document_id: str):
        self._delete_by_filter({"document_id": document_id})

    def delete_by_document_id_list(self, document_id_list: List[str]):
        if not document_id_list:
            return True
        self._delete_by_filter({"document_id__in": document_id_list})
        return True

    def delete_by_source_id(self, source_id: str, source_type: str):
        self._delete_by_filter({"source_id": source_id, "source_type": source_type})

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        self._delete_by_filter({"source_id__in": source_ids, "source_type": source_type})

    def delete_by_paragraph_id(self, paragraph_id: str):
        self._delete_by_filter({"paragraph_id": paragraph_id})

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        self._delete_by_filter({"paragraph_id__in": paragraph_ids})

    # ------------------------------------------------------------------ #
    # 更新（PG 元数据 + Milvus 镜像同步）
    # ------------------------------------------------------------------ #
    def _query_records(self, knowledge_id: str, ids: List[str], output_fields: List[str]) -> List[Dict]:
        """按 id 从 Milvus 取记录（含向量），用于更新时回取向量。"""
        if not ids or not self._has_collection(knowledge_id, raise_on_error=True):
            return []
        records = []
        for i in range(0, len(ids), 1000):
            batch = ids[i : i + 1000]
            data = self._post_required(
                _PATH_QUERY,
                {
                    "collectionName": self._collection_name(knowledge_id),
                    "filter": f"id in {self._str_list(batch)}",
                    "outputFields": list(dict.fromkeys(["id", *output_fields])),
                    "limit": len(batch),
                    "consistencyLevel": "Strong",
                },
            )
            if not isinstance(data.get("data"), list):
                raise AppApiException(500, "Invalid Milvus query response: expected a record list")
            records.extend(data["data"])
        return records

    @transaction.atomic
    def _update_by_filter(self, filter_kwargs: Dict, instance: Dict):
        matched = list(
            QuerySet(Embedding)
            .select_for_update()
            .filter(**filter_kwargs)
            .values(
                "id",
                "knowledge_id",
                "document_id",
                "paragraph_id",
                "is_active",
                "source_id",
                "source_type",
                "embedding",
            )
        )
        if not matched:
            return
        # Copy first; failed queries or writes must leave PG ownership and source vectors intact.
        by_source = self._sync_update(matched, instance)
        pg_instance = {k: v for k, v in instance.items() if k != "embedding"}
        if "embedding" in instance:
            # A successfully replaced vector must no longer compete with its historical PG value.
            pg_instance["embedding"] = None
        if pg_instance:
            QuerySet(Embedding).filter(id__in=[row["id"] for row in matched]).update(**pg_instance)
        for source_kid, ids in by_source.items():
            # Document/paragraph moves wrap this in a larger transaction, which may still roll back.
            transaction.on_commit(partial(self._delete_moved_ids, source_kid, ids))

    @transaction.atomic
    def _delete_moved_ids(self, source_kid: str, ids: List[str]):
        # A subsequent move back may commit before this callback acquires the row locks.
        rows = QuerySet(Embedding).select_for_update().filter(id__in=ids).values("id", "knowledge_id")
        moved_ids = [str(row["id"]) for row in rows if str(row["knowledge_id"]) != source_kid]
        if moved_ids:
            self._delete_ids(source_kid, moved_ids)

    def _sync_update(self, matched_rows: List[Dict], instance: Dict):
        if not matched_rows:
            return {}
        has_embedding = "embedding" in instance
        new_embedding = instance.get("embedding")
        knowledge_changed = "knowledge_id" in instance
        # 未提供新向量时，从 Milvus 取回现有向量用于整体 upsert
        emb_map = {}
        if not has_embedding:
            need = defaultdict(list)
            for r in matched_rows:
                need[str(r["knowledge_id"])].append(str(r["id"]))
            for kid, ids in need.items():
                recs = self._query_records(kid, ids, ["embedding"])
                for rec in recs:
                    emb_map[str(rec.get("id"))] = rec.get("embedding")
        # 按目标 collection 分组 upsert
        by_target = defaultdict(list)
        by_source = defaultdict(list)
        for r in matched_rows:
            target_kid = str(instance["knowledge_id"]) if knowledge_changed else str(r["knowledge_id"])
            emb = new_embedding if has_embedding else emb_map.get(str(r["id"]))
            if not emb:
                if not has_embedding and r.get("embedding") is not None:
                    # Historical PG-only vectors remain available through PG fallback after a move.
                    continue
                raise AppApiException(500, f"Milvus vector missing for embedding {r['id']}; update aborted")
            by_target[target_kid].append(
                {
                    "id": str(r["id"]),
                    "embedding": [float(x) for x in emb],
                    "document_id": str(instance.get("document_id", r["document_id"]) or ""),
                    "paragraph_id": str(r["paragraph_id"]),
                    "is_active": bool(instance.get("is_active", r["is_active"])),
                    "source_id": str(instance.get("source_id", r["source_id"]) or ""),
                    "source_type": int(instance.get("source_type", r["source_type"])),
                }
            )
            if str(r["knowledge_id"]) != target_kid:
                by_source[str(r["knowledge_id"])].append(str(r["id"]))
        for target_kid, recs in by_target.items():
            self._upsert_records(target_kid, recs)
        return by_source

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        self._update_by_filter({"paragraph_id": paragraph_id}, instance)

    def update_by_paragraph_ids(self, paragraph_ids, instance: Dict):
        self._update_by_filter({"paragraph_id__in": paragraph_ids}, instance)

    def update_by_source_id(self, source_id: str, instance: Dict):
        self._update_by_filter({"source_id": source_id}, instance)

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        self._update_by_filter({"source_id__in": source_ids}, instance)

    # ------------------------------------------------------------------ #
    # 检索
    # ------------------------------------------------------------------ #
    @staticmethod
    def _str_list(items) -> str:
        safe = [str(i).replace('"', "") for i in items]
        return '["' + '","'.join(safe) + '"]'

    def _build_search_expr(self, is_active, document_id_list, exclude_document_id_list, exclude_paragraph_list) -> str:
        parts = [f"is_active == {'true' if is_active else 'false'}"]
        if document_id_list:
            parts.append(f"document_id in {self._str_list(document_id_list)}")
        if exclude_document_id_list:
            parts.append(f"document_id not in {self._str_list(exclude_document_id_list)}")
        if exclude_paragraph_list:
            parts.append(f"paragraph_id not in {self._str_list(exclude_paragraph_list)}")
        return " and ".join(parts)

    def _milvus_search(
        self,
        knowledge_id: str,
        query_embedding: List[float],
        top_n: int,
        is_active,
        document_id_list,
        exclude_document_id_list,
        exclude_paragraph_list,
    ) -> List[Dict]:
        if not self._has_collection(knowledge_id):
            return []
        body = {
            "collectionName": self._collection_name(knowledge_id),
            "data": [query_embedding],
            "annsField": "embedding",
            "limit": min(top_n * 10, 500),
            "filter": self._build_search_expr(
                is_active, document_id_list, exclude_document_id_list, exclude_paragraph_list
            ),
            "outputFields": ["paragraph_id"],
            "searchParams": {"metricType": "COSINE", "params": {"ef": max(64, top_n * 10)}},
        }
        # Milvus metadata may lag a move, disable or deletion. PG is authoritative.
        scope = (
            QuerySet(Embedding)
            .filter(
                knowledge_id=knowledge_id,
                is_active=is_active,
                paragraph__knowledge_id=knowledge_id,
                paragraph__document_id=F("document_id"),
                paragraph__is_active=is_active,
            )
            .exclude(paragraph__local_state=LocalState.DELETED)
        )
        if document_id_list:
            scope = scope.filter(document_id__in=document_id_list)
        if exclude_document_id_list:
            scope = scope.exclude(document_id__in=exclude_document_id_list)
        if exclude_paragraph_list:
            scope = scope.exclude(paragraph_id__in=exclude_paragraph_list)
        candidate_limit = body["limit"]
        search_filter = body["filter"]
        seen = set()
        out = []
        while len(out) < candidate_limit:
            body["limit"] = candidate_limit - len(out)
            if seen:
                body["filter"] = f"{search_filter} and id not in {self._str_list(sorted(seen))}"
            ok, data = self._post(_PATH_SEARCH, body)
            if not ok:
                break
            hits = data.get("data") or []
            ids = {str(hit.get("id") or "") for hit in hits} - seen
            if not ids:
                break
            seen.update(ids)
            metadata_by_id = {
                str(row["id"]): row
                for row in scope.filter(id__in=ids).values("id", "paragraph_id", "source_id", "source_type", "meta")
            }
            for hit in hits:
                metadata = metadata_by_id.pop(str(hit.get("id") or ""), None)
                if metadata is None:
                    continue
                # COSINE distance is similarity, matching PG's (1 - cosine_distance).
                out.append(
                    {
                        **metadata,
                        "id": str(metadata["id"]),
                        "paragraph_id": str(metadata["paragraph_id"]),
                        "similarity": float(hit.get("distance", 0)),
                    }
                )
            if len(hits) < body["limit"]:
                break
        return out

    def _dispatch_search(
        self,
        query_text,
        query_embedding,
        knowledge_id_list,
        document_id_list,
        exclude_document_id_list,
        exclude_paragraph_list,
        is_active,
        top_n,
        similarity,
        search_mode: SearchMode,
    ):
        if not knowledge_id_list:
            return []
        if search_mode == SearchMode.keywords:
            return self._search_keywords(
                query_text,
                query_embedding,
                knowledge_id_list,
                document_id_list,
                exclude_document_id_list,
                exclude_paragraph_list,
                is_active,
                top_n,
                similarity,
            )
        if search_mode == SearchMode.blend:
            return self._search_blend(
                query_text,
                query_embedding,
                knowledge_id_list,
                document_id_list,
                exclude_document_id_list,
                exclude_paragraph_list,
                is_active,
                top_n,
                similarity,
            )
        # 默认 / embedding
        return self._search_embedding(
            query_embedding,
            knowledge_id_list,
            document_id_list,
            exclude_document_id_list,
            exclude_paragraph_list,
            is_active,
            top_n,
            similarity,
        )

    def _search_embedding(
        self,
        query_embedding,
        knowledge_id_list,
        document_id_list,
        exclude_document_id_list,
        exclude_paragraph_list,
        is_active,
        top_n,
        similarity,
    ) -> List[Dict]:
        all_results = []
        for kid in knowledge_id_list:
            all_results.extend(
                self._milvus_search(
                    kid,
                    query_embedding,
                    top_n,
                    is_active,
                    document_id_list,
                    exclude_document_id_list,
                    exclude_paragraph_list,
                )
            )
        # PG 存量兜底召回（向量仍在 PG 的老段，Milvus 无对应 collection 时由此覆盖）
        all_results.extend(
            pg_vector_recall(
                query_embedding,
                knowledge_id_list,
                is_active,
                document_id_list,
                exclude_document_id_list,
                exclude_paragraph_list,
                top_n,
            )
        )
        return self._dedupe_and_rank(all_results, similarity, top_n, use_similarity=True)

    def _search_keywords(
        self,
        query_text,
        query_embedding,
        knowledge_id_list,
        document_id_list,
        exclude_document_id_list,
        exclude_paragraph_list,
        is_active,
        top_n,
        similarity,
    ) -> List[Dict]:
        # 关键词检索完全复用 PG tsvector（元数据仍在 PG）
        qs = QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list, is_active=is_active)
        if document_id_list:
            qs = qs.filter(document_id__in=document_id_list)
        if exclude_document_id_list:
            qs = qs.exclude(document_id__in=exclude_document_id_list)
        if exclude_paragraph_list:
            qs = qs.exclude(paragraph_id__in=exclude_paragraph_list)
        return KeywordsSearch().handle(
            qs, query_text, query_embedding, top_n, similarity, SearchMode.keywords, knowledge_id_list
        )

    def _search_blend(
        self,
        query_text,
        query_embedding,
        knowledge_id_list,
        document_id_list,
        exclude_document_id_list,
        exclude_paragraph_list,
        is_active,
        top_n,
        similarity,
    ) -> List[Dict]:
        # 1. Milvus 向量召回候选
        candidates = []
        for kid in knowledge_id_list:
            candidates.extend(
                self._milvus_search(
                    kid,
                    query_embedding,
                    top_n,
                    is_active,
                    document_id_list,
                    exclude_document_id_list,
                    exclude_paragraph_list,
                )
            )
        # PG 存量兜底召回（向量仍在 PG 的老段）
        candidates.extend(
            pg_vector_recall(
                query_embedding,
                knowledge_id_list,
                is_active,
                document_id_list,
                exclude_document_id_list,
                exclude_paragraph_list,
                top_n,
            )
        )
        if not candidates:
            return []
        # 2. PG 文本分（ts_rank_cd）回查
        rank_map = text_rank_by_ids([c["id"] for c in candidates], query_text, knowledge_id_list)
        # 3. 融合：(1 - distance) + ts_rank_cd，等价于原 blend_search.sql 语义
        for c in candidates:
            text_rank = (rank_map.get(c["id"]) or {}).get("text_rank") or 0
            c["comprehensive_score"] = c["similarity"] + float(text_rank)
            # 与 PG blend_search.sql 口径对齐：similarity 即 comprehensive_score
            c["similarity"] = c["comprehensive_score"]
        return self._dedupe_and_rank(candidates, similarity, top_n, use_similarity=False)

    @staticmethod
    def _dedupe_and_rank(results: List[Dict], similarity: float, top_n: int, use_similarity: bool) -> List[Dict]:
        by_para = {}
        for r in results:
            pid = r.get("paragraph_id")
            if not pid:
                continue
            score = r.get("similarity") if use_similarity else r.get("comprehensive_score")
            cur = by_para.get(pid)
            if cur is None or score > (cur.get("similarity") if use_similarity else cur.get("comprehensive_score")):
                r["comprehensive_score"] = r.get("comprehensive_score", score)
                r["similarity"] = r.get("similarity", score)
                by_para[pid] = r
        ranked = list(by_para.values())
        ranked = [
            r for r in ranked if (r.get("similarity") if use_similarity else r.get("comprehensive_score")) > similarity
        ]
        ranked.sort(key=lambda x: x.get("similarity") if use_similarity else x.get("comprehensive_score"), reverse=True)
        return ranked[:top_n]

    def query(
        self,
        query_text: str,
        query_embedding: List[float],
        knowledge_id_list: list[str],
        document_id_list: list[str] | None,
        exclude_document_id_list: list[str],
        exclude_paragraph_list: list[str],
        is_active: bool,
        top_n: int,
        similarity: float,
        search_mode: SearchMode,
    ):
        return self._dispatch_search(
            query_text,
            query_embedding,
            knowledge_id_list,
            document_id_list,
            exclude_document_id_list,
            exclude_paragraph_list,
            is_active,
            top_n,
            similarity,
            search_mode,
        )

    def hit_test(
        self,
        query_text,
        knowledge_id: list[str],
        exclude_document_id_list: list[str],
        top_number: int,
        similarity: float,
        search_mode: SearchMode,
        embedding: MaxKBBaseEmbeddingModel,
        image_list: list[str] | None = None,
        document_id_list: list[str] | None = None,
        exclude_paragraph_id_list: list[str] | None = None,
    ):
        if not knowledge_id or document_id_list == []:
            return []
        image_list = list(image_list or [])
        query_text = normalize_for_embedding(query_text)

        if image_list and not embedding.supports_image_embedding():
            raise AppApiException(500, _("The current embedding model does not support image embedding"))

        query_units = []
        if search_mode == SearchMode.keywords:
            if not query_text:
                return []
            query_units.append({"type": "text", "embedding": []})
        else:
            if query_text:
                query_units.append({"type": "text", "embedding": embedding.embed_query(query_text)})
            if image_list:
                image_embeddings = embedding.embed_images(image_list)
                if len(image_embeddings) != len(image_list):
                    raise AppApiException(500, _("The image embedding model returned an incomplete result"))
                query_units.extend({"type": "image", "embedding": value} for value in image_embeddings)

        # 与 PG 检索一致：分别查询文本和每张图片，保留每个段落得分最高的命中单元。
        best_result_by_paragraph = {}
        for query_unit_index, query_unit in enumerate(query_units):
            unit_search_mode = search_mode
            if query_unit["type"] == "image" and search_mode == SearchMode.blend:
                unit_search_mode = SearchMode.embedding
            results = self._dispatch_search(
                query_text,
                query_unit["embedding"],
                knowledge_id,
                document_id_list,
                exclude_document_id_list,
                exclude_paragraph_id_list,
                True,
                top_number,
                similarity,
                unit_search_mode,
            )
            for result in results:
                paragraph_id = str(result.get("paragraph_id"))
                score = result.get("comprehensive_score", result.get("similarity", 0)) or 0
                previous = best_result_by_paragraph.get(paragraph_id)
                previous_score = (
                    previous.get("comprehensive_score", previous.get("similarity", 0)) or 0
                    if previous is not None
                    else 0
                )
                if previous is None or score > previous_score:
                    best_result_by_paragraph[paragraph_id] = {
                        **result,
                        "query_unit_type": query_unit["type"],
                        "query_unit_index": query_unit_index,
                    }

        result_list = list(best_result_by_paragraph.values())
        result_list.sort(
            key=lambda item: item.get("comprehensive_score", item.get("similarity", 0)) or 0,
            reverse=True,
        )
        return result_list[:top_number]
