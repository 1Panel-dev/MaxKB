# coding=utf-8
"""
PageIndex检索器
提供基于树结构的两阶段检索功能，支持：
1. 章节路径展示
2. 按章节过滤搜索
3. 同章节结果聚合
"""
import time
from typing import List, Dict, Optional
from collections import defaultdict
from django.db.models import QuerySet, Q

from common.utils.logger import maxkb_logger
from knowledge.models import PageIndexNode, Embedding, SearchMode
from knowledge.vector.pg_vector import EmbeddingSearch, KeywordsSearch, BlendSearch


class PageIndexRetriever:
    """PageIndex检索器"""

    def __init__(
        self,
        knowledge_id: str,
        use_tree_filter: bool = True,
        search_mode: str = 'blend',
        top_n: int = 5,
        similarity_threshold: float = 0.6,
        section_filter: Optional[List[str]] = None,
        aggregate_by_section: bool = False
    ):
        """
        Args:
            knowledge_id: 知识库ID
            use_tree_filter: 是否使用树过滤（基础版：True表示按树节点过滤）
            search_mode: 检索模式 ('embedding', 'keywords', 'blend')
            top_n: 最终返回数量
            similarity_threshold: 相似度阈值
            section_filter: 章节过滤列表（节点ID列表），只搜索这些章节下的内容
            aggregate_by_section: 是否按章节聚合结果
        """
        self.knowledge_id = knowledge_id
        self.use_tree_filter = use_tree_filter
        # 确保 search_mode 是有效的检索模式（embedding/keywords/blend）
        # 如果传入 page_index，则默认使用 blend
        if search_mode not in ('embedding', 'keywords', 'blend'):
            search_mode = 'blend'
        self.search_mode_str = search_mode
        # 将字符串转换为SearchMode枚举
        self.search_mode = SearchMode(search_mode)
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold
        self.section_filter = section_filter
        self.aggregate_by_section = aggregate_by_section

        # 缓存节点信息
        self._node_cache: Dict[str, Dict] = {}
    
    def query(
        self,
        query_text: str,
        query_embedding: List[float],
        top_n: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        PageIndex查询（两阶段检索）

        Args:
            query_text: 查询文本
            query_embedding: 查询向量
            top_n: 返回数量（覆盖实例默认值）
            similarity_threshold: 相似度阈值（覆盖实例默认值）

        Returns:
            检索结果列表，每个结果包含：
            - paragraph_id: 段落ID
            - similarity: 相似度分数
            - comprehensive_score: 综合分数
            - section_title: 章节标题
            - section_path: 章节路径（如 "文档 > 第一章 > 1.1节"）
            - tree_level: 树层级
            - tree_path: 树路径ID列表
        """
        top_n = top_n or self.top_n
        similarity_threshold = similarity_threshold or self.similarity_threshold

        start_time = time.time()
        maxkb_logger.info(
            f"[PageIndex][检索] 开始检索 knowledge_id={self.knowledge_id} "
            f"mode={self.search_mode_str} top_n={top_n} threshold={similarity_threshold} "
            f"use_tree_filter={self.use_tree_filter} section_filter={self.section_filter} "
            f"aggregate={self.aggregate_by_section}"
        )

        # 预加载节点缓存
        self._load_node_cache()

        # 阶段1：树过滤（获取候选节点）
        candidate_nodes = self._tree_filter(query_text)

        # 阶段2：向量搜索（精选）
        results = self._vector_search(
            candidate_nodes,
            query_text,
            query_embedding,
            similarity_threshold
        )

        # 阶段3：添加章节路径信息
        results = self._enrich_with_section_info(results)

        # 阶段4：按章节聚合（可选）
        if self.aggregate_by_section:
            results = self._aggregate_by_section(results, top_n)
        else:
            results = results[:top_n]

        cost_ms = int((time.time() - start_time) * 1000)
        maxkb_logger.info(
            f"[PageIndex][检索] 完成检索 knowledge_id={self.knowledge_id} "
            f"result_count={len(results)} cost_ms={cost_ms}"
        )

        return results

    def _load_node_cache(self):
        """预加载节点信息到缓存"""
        if self._node_cache:
            return

        nodes = PageIndexNode.objects.filter(
            knowledge_id=self.knowledge_id
        ).values('id', 'title', 'level', 'path', 'order', 'parent_id', 'document_id')

        for node in nodes:
            self._node_cache[str(node['id'])] = node

    def _get_section_path_string(self, node_id: str) -> str:
        """
        获取章节的完整路径字符串
        例如: "文档标题 > 第一章 > 1.1节"
        """
        if not node_id or node_id not in self._node_cache:
            return ""

        node = self._node_cache[node_id]
        path_ids = node.get('path', [])

        if not path_ids:
            return node.get('title', '') or ''

        # 构建路径字符串
        path_titles = []
        for pid in path_ids:
            pid_str = str(pid)
            if pid_str in self._node_cache:
                title = self._node_cache[pid_str].get('title', '')
                if title:
                    path_titles.append(title)

        # 添加当前节点标题
        current_title = node.get('title', '')
        if current_title:
            path_titles.append(current_title)

        return ' > '.join(path_titles) if path_titles else ''

    def _enrich_with_section_info(self, results: List[Dict]) -> List[Dict]:
        """
        为检索结果添加章节路径信息
        """
        if not results:
            return results

        # 获取所有 paragraph_id 对应的 embedding 信息
        paragraph_ids = [r.get('paragraph_id') for r in results if r.get('paragraph_id')]
        if not paragraph_ids:
            return results

        # 查询 embedding 表获取 page_index_node_id
        embeddings = Embedding.objects.filter(
            paragraph_id__in=paragraph_ids,
            source_type=1  # PARAGRAPH
        ).values('paragraph_id', 'page_index_node_id', 'tree_level', 'tree_path', 'sibling_index')

        # 构建映射
        embedding_map = {}
        for emb in embeddings:
            para_id = str(emb['paragraph_id'])
            if para_id not in embedding_map:
                embedding_map[para_id] = emb

        # 丰富结果
        enriched_results = []
        for result in results:
            para_id = str(result.get('paragraph_id', ''))
            emb_info = embedding_map.get(para_id, {})

            node_id = str(emb_info.get('page_index_node_id', '')) if emb_info.get('page_index_node_id') else None
            node_info = self._node_cache.get(node_id, {}) if node_id else {}

            enriched_result = {
                **result,
                'section_title': node_info.get('title', ''),
                'section_path': self._get_section_path_string(node_id) if node_id else '',
                'tree_level': emb_info.get('tree_level', 0),
                'tree_path': emb_info.get('tree_path', []),
                'sibling_index': emb_info.get('sibling_index', 0),
                'page_index_node_id': node_id
            }
            enriched_results.append(enriched_result)

        return enriched_results

    def _aggregate_by_section(self, results: List[Dict], top_n: int) -> List[Dict]:
        """
        按章节聚合结果

        将同一章节的段落聚合在一起，返回格式：
        [
            {
                'section_title': '第一章',
                'section_path': '文档 > 第一章',
                'paragraphs': [...],
                'max_similarity': 0.95,
                'paragraph_count': 3
            },
            ...
        ]
        """
        if not results:
            return results

        # 按章节分组
        section_groups = defaultdict(list)
        for result in results:
            # 使用 page_index_node_id 作为分组键，如果没有则使用 'unknown'
            section_key = result.get('page_index_node_id') or 'unknown'
            section_groups[section_key].append(result)

        # 构建聚合结果
        aggregated = []
        for section_key, paragraphs in section_groups.items():
            # 按相似度排序
            paragraphs.sort(key=lambda x: x.get('similarity', 0), reverse=True)

            first_para = paragraphs[0]
            aggregated.append({
                'section_title': first_para.get('section_title', ''),
                'section_path': first_para.get('section_path', ''),
                'tree_level': first_para.get('tree_level', 0),
                'page_index_node_id': section_key if section_key != 'unknown' else None,
                'paragraphs': paragraphs,
                'max_similarity': max(p.get('similarity', 0) for p in paragraphs),
                'avg_similarity': sum(p.get('similarity', 0) for p in paragraphs) / len(paragraphs),
                'paragraph_count': len(paragraphs),
                # 保留第一个段落的信息用于兼容
                'paragraph_id': first_para.get('paragraph_id'),
                'similarity': first_para.get('similarity'),
                'comprehensive_score': first_para.get('comprehensive_score')
            })

        # 按最高相似度排序
        aggregated.sort(key=lambda x: x.get('max_similarity', 0), reverse=True)

        return aggregated[:top_n]
    
    def _tree_filter(self, query_text: str) -> Optional[List[PageIndexNode]]:
        """
        阶段1：树过滤

        返回候选章节节点集合

        策略：
        1. 如果指定了 section_filter，只返回这些章节及其子节点
        2. 否则返回所有 Level 0-2 的节点
        3. 如果 use_tree_filter=False，返回 None（不过滤）
        """
        # 如果指定了章节过滤
        if self.section_filter:
            return self._filter_by_sections(self.section_filter)

        if not self.use_tree_filter:
            maxkb_logger.info(f"[PageIndex][检索] 树过滤关闭，直接全量候选")
            return None  # 不过滤，检索所有文档

        # 策略：返回前3层的所有节点
        nodes = list(PageIndexNode.objects.filter(
            knowledge_id=self.knowledge_id,
            level__lte=2
        ).order_by('level', 'order'))

        maxkb_logger.info(
            f"[PageIndex][检索] 树过滤候选节点数={len(nodes)} level<=2"
        )

        return nodes

    def _filter_by_sections(self, section_ids: List[str]) -> List[PageIndexNode]:
        """
        按指定章节过滤

        返回指定章节及其所有子节点
        """
        if not section_ids:
            return []

        # 获取指定的章节节点
        target_nodes = list(PageIndexNode.objects.filter(
            knowledge_id=self.knowledge_id,
            id__in=section_ids
        ))

        if not target_nodes:
            maxkb_logger.warning(f"[PageIndex][检索] 指定的章节不存在: {section_ids}")
            return []

        # 收集所有目标节点及其子节点
        all_node_ids = set(section_ids)

        # 查找所有子节点（path 包含目标节点ID的节点）
        for node in target_nodes:
            # 查找 path 中包含当前节点的所有子节点
            children = PageIndexNode.objects.filter(
                knowledge_id=self.knowledge_id,
                path__contains=[str(node.id)]
            ).values_list('id', flat=True)
            all_node_ids.update(str(cid) for cid in children)

        # 获取所有相关节点
        result_nodes = list(PageIndexNode.objects.filter(
            id__in=all_node_ids
        ).order_by('level', 'order'))

        maxkb_logger.info(
            f"[PageIndex][检索] 章节过滤: 指定章节={len(section_ids)}, "
            f"包含子节点后={len(result_nodes)}"
        )

        return result_nodes
    
    def _vector_search(
        self,
        candidate_nodes: Optional[List[PageIndexNode]],
        query_text: str,
        query_embedding: List[float],
        similarity_threshold: float
    ) -> List[Dict]:
        """
        阶段2：向量搜索

        在候选节点或全部文档中进行向量检索

        注意：为了避免丢失未关联到节点的embedding，过滤条件包含：
        1. 关联到候选节点的embedding
        2. page_index_node_id 为 NULL 的embedding（fallback）
        """
        # 构建查询集
        query_set = QuerySet(Embedding).filter(
            knowledge_id=self.knowledge_id,
            is_active=True
        )

        # 如果有候选节点，添加树过滤（同时包含未关联节点的embedding）
        if candidate_nodes:
            candidate_ids = [node.id for node in candidate_nodes]
            # 使用 Q 对象组合条件：匹配候选节点 OR page_index_node_id 为空
            query_set = query_set.filter(
                Q(page_index_node__in=candidate_ids) | Q(page_index_node__isnull=True)
            )
            maxkb_logger.info(
                f"[PageIndex][检索] 树过滤生效，候选节点={len(candidate_ids)}（包含未关联节点的embedding）"
            )
        else:
            maxkb_logger.info("[PageIndex][检索] 未启用树过滤或候选为空，走全量检索")

        total_candidates = query_set.count()
        maxkb_logger.info(
            f"[PageIndex][检索] 向量检索候选数={total_candidates} similarity={similarity_threshold}"
        )

        # 根据检索模式执行搜索
        if self.search_mode_str == 'embedding':
            search_engine = EmbeddingSearch()
        elif self.search_mode_str == 'blend':
            search_engine = BlendSearch()
        else:  # keywords
            search_engine = KeywordsSearch()  # fallback

        # 执行搜索
        results = search_engine.handle(
            query_set,
            query_text,
            query_embedding,
            top_number=20,  # 先召回20个，后续截断
            similarity=similarity_threshold,
            search_mode=self.search_mode  # 使用SearchMode枚举
        )

        maxkb_logger.info(
            f"[PageIndex][检索] 向量检索完成，召回数={len(results)}"
        )

        # 添加树结构信息（简化版：暂时跳过复杂处理）
        # TODO: 根据实际返回数据结构调整
        return results
    
    def get_tree_path(self, node_id: str) -> Optional[Dict]:
        """
        获取节点的完整路径信息
        
        Args:
            node_id: 节点ID
            
        Returns:
            路径信息字典
        """
        try:
            node = PageIndexNode.objects.get(id=node_id)
            return {
                'id': str(node.id),
                'level': node.level,
                'title': node.title,
                'path': node.path,
                'full_path': node.get_full_path(),
                'content': node.content,
                'char_count': node.char_count
            }
        except PageIndexNode.DoesNotExist:
            return None
    
    def get_sibling_nodes(self, node_id: str) -> List[Dict]:
        """
        获取兄弟节点（同级其他节点）
        
        Args:
            node_id: 节点ID
            
        Returns:
            兄弟节点列表
        """
        try:
            node = PageIndexNode.objects.get(id=node_id)
            siblings = PageIndexNode.objects.filter(
                knowledge_id=self.knowledge_id,
                parent=node.parent,
                level=node.level
            ).exclude(id=node.id).order_by('order')
            
            return [
                {
                    'id': str(sibling.id),
                    'title': sibling.title,
                    'order': sibling.order
                }
                for sibling in siblings
            ]
        except PageIndexNode.DoesNotExist:
            return []
