# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： pg_vector.py
    @date：2023/10/19 15:28
    @desc:
"""
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List

import uuid_utils.compat as uuid
from django.contrib.postgres.search import SearchVector
from django.db.models import QuerySet, Value
from langchain_core.embeddings import Embeddings

from common.db.search import generate_sql_by_query_dict
from common.db.sql_execute import select_list
from common.utils.common import get_file_content
from common.utils.logger import maxkb_logger
from common.utils.ts_vecto_util import to_ts_vector, to_query
from knowledge.models import Embedding, SearchMode, SourceType, Knowledge, PageIndexNode, Paragraph

from knowledge.vector.base_vector import BaseVectorStore
from maxkb.conf import PROJECT_DIR


class PGVector(BaseVectorStore):

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        if len(source_ids) == 0:
            return
        QuerySet(Embedding).filter(source_id__in=source_ids, source_type=source_type).delete()

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        QuerySet(Embedding).filter(source_id__in=source_ids).update(**instance)

    def vector_is_create(self) -> bool:
        # 项目启动默认是创建好的 不需要再创建
        return True

    def vector_create(self):
        return True

    def _is_page_index_enabled(self, knowledge_id: str) -> bool:
        try:
            from config.page_index_config import PageIndexConfig
            result = PageIndexConfig.is_enabled(knowledge_id)
            maxkb_logger.debug(f'[PageIndex] _is_page_index_enabled({knowledge_id}) = {result}')
            return result
        except Exception as e:
            maxkb_logger.warning(f'[PageIndex] _is_page_index_enabled error: {e}')
            return False

    def _resolve_page_index_node_info(self, paragraph_id: str, document_id: str, knowledge_id: str):
        """
        解析单个段落对应的 PageIndexNode

        匹配策略（按优先级）：
        1. 段落标题精确匹配节点标题
        2. 段落内容包含在节点内容中
        3. Fallback 到文档根节点（level=0）
        """
        if not self._is_page_index_enabled(knowledge_id):
            return None

        paragraph = QuerySet(Paragraph).filter(id=paragraph_id).values('title', 'content').first()
        if not paragraph:
            return None

        para_title = (paragraph.get('title') or '').strip()
        para_content = (paragraph.get('content') or '').strip()

        node_query = QuerySet(PageIndexNode).filter(document_id=document_id)
        node = None

        # 策略1：标题精确匹配
        if para_title:
            node = node_query.filter(title=para_title).order_by('level', 'order').values(
                'id', 'level', 'path', 'order'
            ).first()

        # 策略2：基于内容匹配
        if node is None and para_content:
            content_prefix = para_content[:100]
            nodes_with_content = node_query.exclude(content='').exclude(content__isnull=True).order_by('-level', 'order')
            for n in nodes_with_content:
                if content_prefix in (n.content or ''):
                    node = {
                        'id': n.id,
                        'level': n.level,
                        'path': n.path,
                        'order': n.order
                    }
                    break

        # 策略3：Fallback 到根节点
        if node is None:
            node = node_query.filter(level=0).order_by('order').values(
                'id', 'level', 'path', 'order'
            ).first()

        return node

    def _ensure_page_index_exists(self, document_ids: set, knowledge_id: str):
        """
        确保 PageIndex 节点存在，如果不存在则自动构建
        """
        if not document_ids:
            return

        # 检查是否已有节点
        existing_doc_ids = set(
            str(doc_id) for doc_id in
            QuerySet(PageIndexNode).filter(document_id__in=document_ids).values_list('document_id', flat=True).distinct()
        )

        missing_doc_ids = {str(d) for d in document_ids} - existing_doc_ids
        if not missing_doc_ids:
            return

        # 为缺失的文档构建 PageIndex
        try:
            from knowledge.models import Document, Knowledge
            from knowledge.page_index import PageIndex

            knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
            if not knowledge:
                return

            for doc_id in missing_doc_ids:
                document = QuerySet(Document).filter(id=doc_id).first()
                if document:
                    maxkb_logger.info(f'[PageIndex] Auto building for document {doc_id} before embedding')
                    PageIndex.from_documents(
                        documents=[document],
                        knowledge=knowledge,
                        chunk_size=1000,
                        chunk_overlap=200
                    )
        except Exception as e:
            maxkb_logger.warning(f'[PageIndex] Auto build failed: {e}')

    def _resolve_page_index_node_map(self, text_list: List[Dict]):
        """
        解析段落到 PageIndexNode 的映射关系

        匹配策略（按优先级）：
        1. 段落标题精确匹配节点标题
        2. 段落内容包含在节点内容中（基于内容匹配）
        3. Fallback 到文档根节点（level=0）
        """
        # 注意：source_type 可能是整数(1)或枚举(SourceType.PARAGRAPH)，需要兼容两种情况
        paragraph_ids = [
            row.get('paragraph_id') for row in text_list
            if (row.get('source_type') == SourceType.PARAGRAPH or row.get('source_type') == SourceType.PARAGRAPH.value)
               and row.get('paragraph_id')
        ]
        if not paragraph_ids:
            return {}

        paragraph_list = list(QuerySet(Paragraph).filter(id__in=paragraph_ids).values(
            'id', 'title', 'content', 'document_id', 'knowledge_id'
        ))
        if not paragraph_list:
            return {}

        document_ids = {row.get('document_id') for row in paragraph_list}

        # 获取 knowledge_id（假设同一批次的段落属于同一知识库）
        knowledge_id = str(paragraph_list[0].get('knowledge_id')) if paragraph_list else None

        # 确保 PageIndex 存在
        if knowledge_id and self._is_page_index_enabled(knowledge_id):
            self._ensure_page_index_exists(document_ids, knowledge_id)

        # 重新查询节点（包含 content 用于内容匹配）
        nodes = list(QuerySet(PageIndexNode).filter(document_id__in=document_ids).values(
            'id', 'title', 'level', 'path', 'order', 'document_id', 'content'
        ))
        if not nodes:
            return {}

        # 构建索引结构（统一使用字符串类型的 document_id）
        node_by_title = {}  # (doc_id_str, title) -> node
        root_by_doc = {}    # doc_id_str -> root_node (level=0)
        nodes_by_doc = {}   # doc_id_str -> [nodes] (按 level 排序，用于内容匹配)

        for node in nodes:
            doc_id_str = str(node.get('document_id'))

            # 收集根节点
            if node.get('level') == 0 and doc_id_str not in root_by_doc:
                root_by_doc[doc_id_str] = node

            # 按标题索引
            title = (node.get('title') or '').strip()
            if title:
                node_by_title[(doc_id_str, title)] = node

            # 按文档分组（用于内容匹配）
            if doc_id_str not in nodes_by_doc:
                nodes_by_doc[doc_id_str] = []
            nodes_by_doc[doc_id_str].append(node)

        # 按 level 降序排序（优先匹配更深层的节点）
        for doc_id_str in nodes_by_doc:
            nodes_by_doc[doc_id_str].sort(key=lambda n: -n.get('level', 0))

        node_map = {}

        # 调试日志
        maxkb_logger.info(f'[PageIndex] _resolve_page_index_node_map: paragraph_count={len(paragraph_list)}, nodes_count={len(nodes)}')
        maxkb_logger.info(f'[PageIndex] root_by_doc keys: {list(root_by_doc.keys())}')

        for paragraph in paragraph_list:
            knowledge_id_str = str(paragraph.get('knowledge_id'))
            if not self._is_page_index_enabled(knowledge_id_str):
                maxkb_logger.info(f'[PageIndex] PageIndex not enabled for knowledge {knowledge_id_str}')
                continue

            doc_id_str = str(paragraph.get('document_id'))
            para_id_str = str(paragraph.get('id'))
            para_title = (paragraph.get('title') or '').strip()
            para_content = (paragraph.get('content') or '').strip()

            matched_node = None

            # 策略1：标题精确匹配
            if para_title:
                matched_node = node_by_title.get((doc_id_str, para_title))
                if matched_node:
                    maxkb_logger.debug(f'[PageIndex] Matched by title: para={para_id_str[:8]}, node={matched_node.get("id")}')

            # 策略2：基于内容匹配（段落内容的前100字符在节点内容中）
            if matched_node is None and para_content and doc_id_str in nodes_by_doc:
                content_prefix = para_content[:100]
                for node in nodes_by_doc[doc_id_str]:
                    node_content = node.get('content') or ''
                    if content_prefix in node_content:
                        matched_node = node
                        maxkb_logger.debug(f'[PageIndex] Matched by content: para={para_id_str[:8]}, node={node.get("id")}')
                        break

            # 策略3：Fallback 到根节点
            if matched_node is None:
                matched_node = root_by_doc.get(doc_id_str)
                if matched_node:
                    maxkb_logger.debug(f'[PageIndex] Fallback to root: para={para_id_str[:8]}, node={matched_node.get("id")}')
                else:
                    maxkb_logger.warning(f'[PageIndex] No root node found for doc={doc_id_str}')

            if matched_node:
                node_map[para_id_str] = matched_node
            else:
                maxkb_logger.warning(f'[PageIndex] No match for paragraph {para_id_str}')

        maxkb_logger.info(f'[PageIndex] _resolve_page_index_node_map result: {len(node_map)} paragraphs matched')
        return node_map

    def _save(self, text, source_type: SourceType, knowledge_id: str, document_id: str, paragraph_id: str,
              source_id: str,
              is_active: bool,
              embedding: Embeddings):
        text_embedding = [float(x) for x in embedding.embed_query(text)]
        embedding = Embedding(
            id=uuid.uuid7(),
            knowledge_id=knowledge_id,
            document_id=document_id,
            is_active=is_active,
            paragraph_id=paragraph_id,
            source_id=source_id,
            embedding=text_embedding,
            source_type=source_type,
            search_vector=to_ts_vector(text)
        )
        # 兼容 source_type 为整数或枚举的情况
        is_paragraph = (source_type == SourceType.PARAGRAPH or source_type == SourceType.PARAGRAPH.value)
        if is_paragraph and paragraph_id:
            node_info = self._resolve_page_index_node_info(paragraph_id, document_id, knowledge_id)
            if node_info:
                embedding.page_index_node_id = node_info.get('id')
                embedding.tree_level = node_info.get('level', 0)
                embedding.tree_path = node_info.get('path', [])
                embedding.sibling_index = node_info.get('order', 0)
        embedding.save()
        return True


    def _batch_save(self, text_list: List[Dict], embedding: Embeddings, is_the_task_interrupted):
        texts = [row.get('text') for row in text_list]
        embeddings = embedding.embed_documents(texts)

        # 调试日志：检查 text_list 的内容
        maxkb_logger.info(f'[PageIndex] _batch_save: text_list count={len(text_list)}')
        if text_list:
            sample = text_list[0]
            maxkb_logger.info(f'[PageIndex] _batch_save sample: source_type={sample.get("source_type")} (type={type(sample.get("source_type")).__name__}), paragraph_id={sample.get("paragraph_id")}')

        node_map = self._resolve_page_index_node_map(text_list)
        maxkb_logger.info(f'[PageIndex] _batch_save: node_map size={len(node_map)}')

        embedding_list = []
        matched_count = 0
        for index in range(0, len(texts)):
            row = text_list[index]
            embedding_item = Embedding(
                id=uuid.uuid7(),
                document_id=row.get('document_id'),
                paragraph_id=row.get('paragraph_id'),
                knowledge_id=row.get('knowledge_id'),
                is_active=row.get('is_active', True),
                source_id=row.get('source_id'),
                source_type=row.get('source_type'),
                embedding=[float(x) for x in embeddings[index]],
                search_vector=SearchVector(Value(to_ts_vector(row['text'])))
            )
            # 兼容 source_type 为整数或枚举的情况
            source_type = row.get('source_type')
            is_paragraph = (source_type == SourceType.PARAGRAPH or source_type == SourceType.PARAGRAPH.value)
            if is_paragraph and row.get('paragraph_id'):
                node_info = node_map.get(str(row.get('paragraph_id')))
                if node_info:
                    embedding_item.page_index_node_id = node_info.get('id')
                    embedding_item.tree_level = node_info.get('level', 0)
                    embedding_item.tree_path = node_info.get('path', [])
                    embedding_item.sibling_index = node_info.get('order', 0)
                    matched_count += 1
            embedding_list.append(embedding_item)

        maxkb_logger.info(f'[PageIndex] _batch_save: matched_count={matched_count}/{len(embedding_list)}')

        if not is_the_task_interrupted():
            QuerySet(Embedding).bulk_create(embedding_list) if len(embedding_list) > 0 else None
        return True


    def hit_test(self, query_text, knowledge_id_list: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: Embeddings):
        if knowledge_id_list is None or len(knowledge_id_list) == 0:
            return []
        exclude_dict = {}
        embedding_query = embedding.embed_query(query_text)
        query_set = QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list, is_active=True)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            exclude_dict.__setitem__('document_id__in', exclude_document_id_list)
        query_set = query_set.exclude(**exclude_dict)

        page_index_results = self._try_page_index_search(
            knowledge_id_list,
            query_text,
            embedding_query,
            top_number,
            similarity,
            search_mode
        )
        if page_index_results is not None:
            return page_index_results

        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                return search_handle.handle(query_set, query_text, embedding_query, top_number, similarity, search_mode)

        return []


    def query(self, query_text: str, query_embedding: List[float], knowledge_id_list: list[str],
              document_id_list: list[str],
              exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float,
              search_mode: SearchMode):
        exclude_dict = {}
        if knowledge_id_list is None or len(knowledge_id_list) == 0:
            return []
        query_set = QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list, is_active=is_active)
        if document_id_list is not None and len(document_id_list) > 0:
            query_set = query_set.filter(document_id__in=document_id_list)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            query_set = query_set.exclude(document_id__in=exclude_document_id_list)
        if exclude_paragraph_list is not None and len(exclude_paragraph_list) > 0:
            query_set = query_set.exclude(paragraph_id__in=exclude_paragraph_list)
        query_set = query_set.exclude(**exclude_dict)

        # 【方案B】检查是否启用PageIndex检索模式
        page_index_results = self._try_page_index_search(
            knowledge_id_list,
            query_text,
            query_embedding,
            top_n,
            similarity,
            search_mode
        )
        if page_index_results is not None:
            return page_index_results

        # 回退到传统检索模式
        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                return search_handle.handle(query_set, query_text, query_embedding, top_n, similarity, search_mode)

    def _try_page_index_search(
        self,
        knowledge_id_list: list[str],
        query_text: str,
        query_embedding: List[float],
        top_n: int,
        similarity: float,
        search_mode: SearchMode,
        section_filter: List[str] = None,
        aggregate_by_section: bool = False
    ):
        """
        尝试使用PageIndex检索（方案B）

        检查知识库是否配置了PageIndex检索模式，如果是则使用PageIndex检索

        Args:
            knowledge_id_list: 知识库ID列表
            query_text: 查询文本
            query_embedding: 查询向量
            top_n: 返回数量
            similarity: 相似度阈值
            search_mode: 检索模式
            section_filter: 章节过滤列表（节点ID列表），只搜索这些章节下的内容
            aggregate_by_section: 是否按章节聚合结果

        Returns:
            PageIndex检索结果，如果未启用则返回None
        """
        try:
            from knowledge.models import Knowledge
            from knowledge.page_index.page_index_retriever import PageIndexRetriever

            # 获取第一个知识库（简化处理，假设只有一个知识库）
            knowledge = Knowledge.objects.filter(id__in=knowledge_id_list).first()
            if not knowledge:
                return None

            try:
                from config.page_index_config import PageIndexConfig
                if not PageIndexConfig.is_enabled(str(knowledge.id)):
                    return None
            except Exception:
                return None

            meta = knowledge.meta or {}
            # 检查知识库是否配置了PageIndex检索模式
            search_mode_config = meta.get('search_mode', 'traditional')
            if search_mode_config != 'page_index':
                return None  # 未启用PageIndex检索模式


            # 检查PageIndexNode是否有数据
            from knowledge.models import PageIndexNode
            page_index_count = PageIndexNode.objects.filter(
                knowledge_id=knowledge.id
            ).count()

            if page_index_count == 0:
                # PageIndex未构建，回退到传统检索
                return None

            # 使用PageIndex检索
            # 注意：page_index 是检索类型，不是检索模式
            # 检索模式应该是 embedding/keywords/blend，从 meta 配置读取或默认使用 blend
            search_mode_str = meta.get('inner_search_mode', 'blend')
            # 如果传入的 search_mode 是有效的检索模式（非 page_index），则使用传入值
            if search_mode and search_mode.value in ('embedding', 'keywords', 'blend'):
                search_mode_str = search_mode.value
            use_tree_filter = meta.get('use_tree_filter', True)
            meta_top_n = meta.get('top_n', top_n)
            meta_similarity = meta.get('similarity_threshold', similarity)
            # 从 meta 获取聚合配置，或使用传入参数
            meta_aggregate = meta.get('aggregate_by_section', aggregate_by_section)

            retriever = PageIndexRetriever(
                knowledge_id=str(knowledge.id),
                use_tree_filter=use_tree_filter,
                search_mode=search_mode_str,
                top_n=meta_top_n,
                similarity_threshold=meta_similarity,
                section_filter=section_filter,
                aggregate_by_section=meta_aggregate
            )


            results = retriever.query(
                query_text=query_text,
                query_embedding=query_embedding,
                top_n=meta_top_n,
                similarity_threshold=meta_similarity
            )


            return results

        except Exception as e:
            maxkb_logger.warning(f'[PageIndex] Search failed: {e}')
            # PageIndex检索失败，回退到传统检索
            return None

    def update_by_source_id(self, source_id: str, instance: Dict):
        QuerySet(Embedding).filter(source_id=source_id).update(**instance)

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).update(**instance)

    def update_by_paragraph_ids(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_id).update(**instance)

    def delete_by_knowledge_id(self, knowledge_id: str):
        QuerySet(Embedding).filter(knowledge_id=knowledge_id).delete()

    def delete_by_knowledge_id_list(self, knowledge_id_list: List[str]):
        QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list).delete()

    def delete_by_document_id(self, document_id: str):
        QuerySet(Embedding).filter(document_id=document_id).delete()
        return True

    def delete_by_document_id_list(self, document_id_list: List[str]):
        if len(document_id_list) == 0:
            return True
        return QuerySet(Embedding).filter(document_id__in=document_id_list).delete()

    def delete_by_source_id(self, source_id: str, source_type: str):
        QuerySet(Embedding).filter(source_id=source_id, source_type=source_type).delete()
        return True

    def delete_by_paragraph_id(self, paragraph_id: str):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).delete()

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_ids).delete()


class ISearch(ABC):
    @abstractmethod
    def support(self, search_mode: SearchMode):
        pass

    @abstractmethod
    def handle(self, query_set, query_text, query_embedding, top_number: int,
               similarity: float, search_mode: SearchMode):
        pass


class EmbeddingSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql',
                                                                            'embedding_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql, [
            len(query_embedding),
            json.dumps(query_embedding),
            *exec_params,
            similarity,
            top_number
        ])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.embedding.value


class KeywordsSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'keywords_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql',
                                                                            'keywords_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql, [
            to_query(query_text),
            *exec_params,
            similarity,
            top_number
        ])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.keywords.value


class BlendSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql',
                                                                            'blend_search.sql')),
                                                           with_table_name=True)

        # 动态调整权重：短查询大幅提高关键词权重
        query_length = len(query_text.strip())
        if query_length <= 10:
            # 极短查询（如"CTO"、"CTO是谁？"）：关键词权重占主导
            vector_weight = 0.2
            keyword_weight = 0.8
        elif query_length <= 20:
            # 短查询：关键词权重较高
            vector_weight = 0.4
            keyword_weight = 0.6
        else:
            # 长查询：向量权重较高
            vector_weight = 0.6
            keyword_weight = 0.4

        embedding_model = select_list(exec_sql, [
            vector_weight,  # Vector weight (dynamic)
            keyword_weight,  # Keyword weight (dynamic)
            vector_weight,  # Vector weight for comprehensive_score
            keyword_weight,  # Keyword weight for comprehensive_score
            len(query_embedding),
            json.dumps(query_embedding),
            to_query(query_text),
            *exec_params, similarity,
            top_number
        ])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.blend.value


search_handle_list = [EmbeddingSearch(), KeywordsSearch(), BlendSearch()]
