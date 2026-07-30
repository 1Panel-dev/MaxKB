# coding=utf-8
"""
@project: maxkb
@file： pg_fulltext.py
@desc: PG 全文检索复用 helper。混合存储下，元数据 + tsvector 仍在 PG，
       Milvus 等外部向量库的 keywords / blend 检索可复用这里的 PG 全文能力。
"""

import json
import os
from typing import Dict, List

from common.db.search import generate_sql_by_query_dict
from common.db.sql_execute import select_list
from common.utils.common import get_file_content
from common.utils.ts_vecto_util import to_query
from django.db.models import QuerySet
from knowledge.models import Embedding, Termbase
from maxkb.conf import PROJECT_DIR


def text_rank_by_ids(embedding_ids: List[str], query_text: str, knowledge_id_list: list[str] | None) -> Dict[str, dict]:
    """
    给定一批 embedding id，计算其在 PG tsvector 上的文本相关性得分，
    供 blend 检索与 Milvus 向量召回结果融合使用。

    :param embedding_ids:    embedding 主键 id 列表
    :param query_text:       原始查询文本（未分词）
    :param knowledge_id_list: 知识库 id 列表，用于术语表加权
    :return: {id: {"id", "paragraph_id", "text_rank"}}
    """
    if not embedding_ids:
        return {}
    query_set = QuerySet(Embedding).filter(id__in=embedding_ids)
    exec_sql, exec_params = generate_sql_by_query_dict(
        {"embedding_query": query_set},
        select_string=get_file_content(os.path.join(PROJECT_DIR, "apps", "knowledge", "sql", "blend_text_rank.sql")),
        with_table_name=True,
    )
    terms = (
        list(QuerySet(Termbase).filter(knowledge_id__in=knowledge_id_list).values_list("content", flat=True))
        if knowledge_id_list
        else None
    )
    rows = select_list(exec_sql, [to_query(query_text, user_words=terms), *exec_params])
    return {row["id"]: row for row in rows}


def pg_vector_recall(
    query_embedding: List[float],
    knowledge_id_list: list[str],
    is_active,
    document_id_list,
    exclude_document_id_list,
    exclude_paragraph_list,
    top_n: int,
) -> List[Dict]:
    """
    PG 向量召回（双查兜底）：按 query_embedding 在 PG embedding 列做最近邻检索，
    返回 PG 向量命中及 source_id、source_type、meta，供图片展示与召回统计使用。

    Milvus 模式下新增文本向量的 PG embedding 列为 NULL；历史文本及图片向量仍在 PG，
    由此统一召回，再与 Milvus 命中按段落合并。
    """
    if not knowledge_id_list:
        return []
    qs = QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list, is_active=is_active)
    if document_id_list:
        qs = qs.filter(document_id__in=document_id_list)
    if exclude_document_id_list:
        qs = qs.exclude(document_id__in=exclude_document_id_list)
    if exclude_paragraph_list:
        qs = qs.exclude(paragraph_id__in=exclude_paragraph_list)
    exec_sql, exec_params = generate_sql_by_query_dict(
        {"embedding_query": qs},
        select_string=get_file_content(os.path.join(PROJECT_DIR, "apps", "knowledge", "sql", "embedding_recall.sql")),
        with_table_name=True,
    )
    rows = select_list(
        exec_sql,
        [
            len(query_embedding),
            json.dumps(query_embedding),
            *exec_params,
            len(query_embedding),
            json.dumps(query_embedding),
            top_n,
        ],
    )
    return [
        {
            "id": str(row["id"]),
            "paragraph_id": str(row["paragraph_id"]),
            "source_id": row["source_id"],
            "source_type": row["source_type"],
            "meta": row["meta"],
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]
