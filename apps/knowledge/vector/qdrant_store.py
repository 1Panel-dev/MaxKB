# coding=utf-8
"""
@project: maxkb
@file: qdrant_store.py
@desc: Qdrant vector store implementation
"""
import hashlib
import logging
import uuid as uuid_lib
from typing import Dict, List

from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from knowledge.models import SearchMode
from knowledge.vector.base_vector import BaseVectorStore, normalize_for_embedding
from maxkb.const import CONFIG

logger = logging.getLogger(__name__)

DISTANCE_MAP = {
    "Cosine": Distance.COSINE,
    "Euclid": Distance.EUCLID,
    "Dot": Distance.DOT,
}


def _build_embedding_id(source_id, source_type, chunk_index=0) -> str:
    """Generate a stable UUID for a point from its source_id, source_type and chunk_index."""
    hash_input = f"{source_id}:{source_type}:{chunk_index}"
    return str(uuid_lib.UUID(hashlib.md5(hash_input.encode()).hexdigest()))


def _make_collection_name(knowledge_id: str) -> str:
    prefix = CONFIG.get("QDRANT_COLLECTION_PREFIX", "maxkb_")
    return f"{prefix}knowledge_{knowledge_id}"


class QdrantVectorStore(BaseVectorStore):
    def __init__(self):
        self._client = None
        self._distance = DISTANCE_MAP.get(
            CONFIG.get("QDRANT_DISTANCE_METRIC", "Cosine"), Distance.COSINE
        )

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                host=CONFIG.get("QDRANT_HOST", "localhost"),
                port=int(CONFIG.get("QDRANT_PORT", 6333)),
                grpc_port=int(CONFIG.get("QDRANT_GRPC_PORT", 6334)),
                api_key=CONFIG.get("QDRANT_API_KEY") or None,
                prefer_grpc=bool(CONFIG.get("QDRANT_PREFER_GRPC", True)),
                timeout=60,
            )
        return self._client

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def vector_is_create(self) -> bool:
        return True

    def vector_create(self):
        return True

    def _ensure_collection(self, knowledge_id: str, vector_size: int = None):
        name = _make_collection_name(knowledge_id)
        collections = {c.name for c in self.client.get_collections().collections}
        if name in collections:
            return
        if vector_size is None:
            vector_size = 768
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=self._distance),
            hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
        )
        # Create payload indexes for filtering
        for field in ["knowledge_id", "document_id", "source_type"]:
            try:
                self.client.create_payload_index(
                    collection_name=name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def _save_prepare(self, text, source_type, knowledge_id, document_id, paragraph_id, source_id, is_active, embedding_model, terms):
        text = normalize_for_embedding(text)
        text_embedding = [float(x) for x in embedding_model.embed_query(text)]
        return {
            "text": text,
            "embedding": text_embedding,
            "source_type": source_type,
            "knowledge_id": knowledge_id,
            "document_id": document_id,
            "paragraph_id": paragraph_id,
            "source_id": source_id,
            "is_active": is_active,
        }

    def _save(
        self,
        text,
        source_type,
        knowledge_id,
        document_id,
        paragraph_id,
        source_id,
        is_active,
        embedding: Embeddings,
    ):
        data = self._save_prepare(
            text, source_type, knowledge_id, document_id, paragraph_id,
            source_id, is_active, embedding, None
        )
        self._upsert_points(knowledge_id, [data])

    def _batch_save(self, text_list: List[Dict], embedding: Embeddings, is_the_task_interrupted):
        if not text_list:
            return True
        texts = [normalize_for_embedding(row.get("text")) for row in text_list]
        embeddings = embedding.embed_documents(texts)

        data_list = []
        for index, row in enumerate(text_list):
            knowledge_id = str(row.get("knowledge_id")) if row.get("knowledge_id") else None
            data_list.append({
                "text": texts[index],
                "embedding": [float(x) for x in embeddings[index]],
                "source_type": row.get("source_type"),
                "knowledge_id": knowledge_id,
                "document_id": str(row.get("document_id")) if row.get("document_id") else None,
                "paragraph_id": str(row.get("paragraph_id")) if row.get("paragraph_id") else None,
                "source_id": str(row.get("source_id")) if row.get("source_id") else None,
                "is_active": row.get("is_active", True),
                "chunk_index": row.get("chunk_index", 0),
                "title": row.get("title", "") or "",
            })

        # Group by knowledge_id
        by_knowledge = {}
        for d in data_list:
            kid = d["knowledge_id"]
            by_knowledge.setdefault(kid, []).append(d)

        for kid, batch in by_knowledge.items():
            if not is_the_task_interrupted():
                self._upsert_points(kid, batch)
        return True

    def _upsert_points(self, knowledge_id: str, data_list: List[Dict]):
        if not data_list:
            return
        vector_size = len(data_list[0]["embedding"])
        self._ensure_collection(knowledge_id, vector_size)

        collection_name = _make_collection_name(knowledge_id)
        points = []
        for d in data_list:
            chunk_index = d.get("chunk_index", 0)
            point_id = _build_embedding_id(d["source_id"], str(d["source_type"]), chunk_index)
            points.append(PointStruct(
                id=point_id,
                vector=d["embedding"],
                payload={
                    "knowledge_id": d["knowledge_id"],
                    "document_id": d["document_id"],
                    "paragraph_id": d["paragraph_id"],
                    "source_id": d["source_id"],
                    "source_type": str(d["source_type"]),
                    "is_active": d.get("is_active", True),
                    "content": d.get("text", ""),
                    "title": d.get("title", "") or "",
                },
            ))

        batch_size = 200
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=collection_name,
                points=points[i : i + batch_size],
                wait=True,
            )

    # ------------------------------------------------------------------
    # 查询 / 搜索
    # ------------------------------------------------------------------

    def search(
        self,
        query_text,
        knowledge_id_list: list[str],
        exclude_document_id_list: list[str],
        exclude_paragraph_list: list[str],
        is_active: bool,
        embedding: Embeddings,
    ):
        if not knowledge_id_list:
            return []
        query_text = normalize_for_embedding(query_text)
        embedding_query = embedding.embed_query(query_text)
        result = self.query(
            query_text, embedding_query, knowledge_id_list, None,
            exclude_document_id_list, exclude_paragraph_list,
            is_active, 1, 3, 0.65,
        )
        return result[0] if result else []

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
        if not knowledge_id_list:
            return ([], [])

        # Use embedding search from Qdrant for all modes
        all_results = []
        for kid in knowledge_id_list:
            results = self._qdrant_search(
                kid, query_embedding, query_text,
                document_id_list, exclude_document_id_list,
                exclude_paragraph_list, top_n, similarity, search_mode,
            )
            all_results.extend(results)

        all_results.sort(
            key=lambda x: x.get("similarity", x.get("comprehensive_score", 0)),
            reverse=True,
        )
        all_results = all_results[:top_n]

        return ([r for r in all_results if r.get("similarity", 0) >= similarity],
                [r for r in all_results if r.get("similarity", 0) < similarity])

    def _qdrant_search(
        self,
        knowledge_id: str,
        query_embedding: List[float],
        query_text: str,
        document_id_list: list[str] | None,
        exclude_document_id_list: list[str],
        exclude_paragraph_list: list[str],
        top_n: int,
        similarity: float,
        search_mode: SearchMode,
    ) -> List[Dict]:
        collection_name = _make_collection_name(knowledge_id)
        try:
            collections = {c.name for c in self.client.get_collections().collections}
            if collection_name not in collections:
                return []
        except Exception:
            return []

        q_filter = self._build_filter(
            document_id_list, exclude_document_id_list, exclude_paragraph_list
        )

        qdrant_response = self.client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            limit=top_n * 2,
            query_filter=q_filter,
            with_payload=True,
        )
        qdrant_results = qdrant_response.points

        results = []
        for r in qdrant_results:
            payload = r.payload or {}
            results.append({
                "id": payload.get("source_id", str(r.id)),
                "similarity": r.score,
                "comprehensive_score": r.score,
                "document_id": payload.get("document_id", ""),
                "paragraph_id": payload.get("paragraph_id", ""),
                "knowledge_id": payload.get("knowledge_id", ""),
                "source_id": payload.get("source_id", ""),
                "source_type": payload.get("source_type", ""),
                "content": payload.get("content", ""),
                "title": payload.get("title", ""),
            })
        return results

    def hit_test(
        self,
        query_text,
        knowledge_id: list[str],
        exclude_document_id_list: list[str],
        top_number: int,
        similarity: float,
        search_mode: SearchMode,
        embedding: Embeddings,
    ):
        if not knowledge_id:
            return []
        exclude_dict = {}
        if exclude_document_id_list:
            exclude_dict["document_id__in"] = exclude_document_id_list

        query_text = normalize_for_embedding(query_text)
        embedding_query = embedding.embed_query(query_text)

        all_results = []
        for kid in knowledge_id:
            results = self._qdrant_search(
                kid, embedding_query, query_text,
                None, exclude_document_id_list, [],
                top_number, similarity, search_mode,
            )
            all_results.extend(results)

        all_results.sort(
            key=lambda x: x.get("similarity", x.get("comprehensive_score", 0)),
            reverse=True,
        )
        return all_results[:top_number]

    # ------------------------------------------------------------------
    # 过滤条件构建
    # ------------------------------------------------------------------

    def _build_filter(
        self,
        document_id_list: list[str] | None,
        exclude_document_id_list: list[str] | None,
        exclude_paragraph_list: list[str] | None,
    ) -> Filter | None:
        must = []
        must_not = []

        if document_id_list:
            must.append(FieldCondition(
                key="document_id",
                match=MatchValue(value=document_id_list[0]),
            ) if len(document_id_list) == 1 else FieldCondition(
                key="document_id",
                match=MatchAny(any=document_id_list),
            ))
        if exclude_document_id_list:
            must_not.append(FieldCondition(
                key="document_id",
                match=MatchValue(value=exclude_document_id_list[0]),
            ) if len(exclude_document_id_list) == 1 else FieldCondition(
                key="document_id",
                match=MatchAny(any=exclude_document_id_list),
            ))
        if exclude_paragraph_list:
            must_not.append(FieldCondition(
                key="paragraph_id",
                match=MatchValue(value=exclude_paragraph_list[0]),
            ) if len(exclude_paragraph_list) == 1 else FieldCondition(
                key="paragraph_id",
                match=MatchAny(any=exclude_paragraph_list),
            ))

        if not must and not must_not:
            return None
        f = Filter()
        if must:
            f.must = must
        if must_not:
            f.must_not = must_not
        return f

    # ------------------------------------------------------------------
    # 更新
    # ------------------------------------------------------------------

    def update_by_source_id(self, source_id: str, instance: Dict):
        for c in self.client.get_collections().collections:
            try:
                self.client.set_payload(
                    collection_name=c.name,
                    payload=instance,
                    points=Filter(
                        must=[FieldCondition(key="source_id", match=MatchValue(value=source_id))]
                    ),
                )
            except Exception:
                pass

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        for c in self.client.get_collections().collections:
            try:
                self.client.set_payload(
                    collection_name=c.name,
                    payload=instance,
                    points=Filter(
                        must=[FieldCondition(key="source_id", match=MatchAny(any=source_ids))]
                    ),
                )
            except Exception:
                pass

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        for c in self.client.get_collections().collections:
            try:
                self.client.set_payload(
                    collection_name=c.name,
                    payload=instance,
                    points=Filter(
                        must=[FieldCondition(key="paragraph_id", match=MatchValue(value=paragraph_id))]
                    ),
                )
            except Exception:
                pass

    def update_by_paragraph_ids(self, paragraph_ids: List[str], instance: Dict):
        for c in self.client.get_collections().collections:
            try:
                self.client.set_payload(
                    collection_name=c.name,
                    payload=instance,
                    points=Filter(
                        must=[FieldCondition(key="paragraph_id", match=MatchAny(any=paragraph_ids))]
                    ),
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 删除
    # ------------------------------------------------------------------

    def delete_by_knowledge_id(self, knowledge_id: str):
        collection_name = _make_collection_name(knowledge_id)
        try:
            self.client.delete_collection(collection_name=collection_name)
        except Exception:
            pass

    def delete_by_knowledge_id_list(self, knowledge_id_list: List[str]):
        for kid in knowledge_id_list:
            self.delete_by_knowledge_id(kid)

    def delete_by_document_id(self, document_id: str):
        self._delete_by_payload_filter("document_id", document_id)
        return True

    def delete_by_document_id_list(self, document_id_list: List[str]):
        if not document_id_list:
            return True
        for did in document_id_list:
            self._delete_by_payload_filter("document_id", did)
        return True

    def delete_by_source_id(self, source_id: str, source_type: str):
        self._delete_by_payload_filter("source_id", source_id)
        return True

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        for sid in source_ids:
            self._delete_by_payload_filter("source_id", sid)

    def delete_by_paragraph_id(self, paragraph_id: str):
        self._delete_by_payload_filter("paragraph_id", paragraph_id)

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        for pid in paragraph_ids:
            self._delete_by_payload_filter("paragraph_id", pid)

    def _delete_by_payload_filter(self, field: str, value: str):
        for c in self.client.get_collections().collections:
            try:
                self.client.delete(
                    collection_name=c.name,
                    points_selector=Filter(
                        must=[FieldCondition(key=field, match=MatchValue(value=value))]
                    ),
                )
            except Exception:
                pass
