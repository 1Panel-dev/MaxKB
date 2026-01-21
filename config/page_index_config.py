# coding=utf-8
"""
PageIndex配置管理
用于管理知识库的PageIndex检索模式配置
"""
from typing import Dict, Optional


class PageIndexConfig:
    """PageIndex配置管理类"""

    # 检索模式枚举
    SEARCH_MODE_TRADITIONAL = 'traditional'  # 传统检索模式
    SEARCH_MODE_PAGE_INDEX = 'page_index'   # PageIndex检索模式

    # 全局开关（默认关闭，需要手动启用）
    # 前端UI已经提供用户切换功能，所以这里启用全局开关
    ENABLE_PAGE_INDEX = True

    # 默认配置
    DEFAULT_CONFIG = {
        'use_tree_filter': True,        # 使用树过滤
        'search_mode': 'blend',           # 检索模式（'embedding', 'keywords', 'blend'）
        'top_n': 5,                       # 返回数量
        'similarity_threshold': 0.6,       # 相似度阈值
    }

    @classmethod
    def is_enabled(cls, knowledge_id: str = None) -> bool:
        """
        检查PageIndex是否全局启用

        Args:
            knowledge_id: 知识库ID（预留参数，可用于按知识库控制）

        Returns:
            是否启用PageIndex
        """
        return cls.ENABLE_PAGE_INDEX

    @classmethod
    def set_enabled(cls, enabled: bool):
        """
        设置PageIndex全局开关

        Args:
            enabled: 是否启用
        """
        cls.ENABLE_PAGE_INDEX = enabled

    @classmethod
    def get_search_mode(cls, knowledge_meta: Dict) -> str:
        """
        获取知识库的检索模式

        Args:
            knowledge_meta: 知识库的meta字典

        Returns:
            检索模式（'traditional' 或 'page_index'）
        """
        if not cls.ENABLE_PAGE_INDEX:
            return cls.SEARCH_MODE_TRADITIONAL

        return knowledge_meta.get('search_mode', cls.SEARCH_MODE_TRADITIONAL)

    @classmethod
    def set_search_mode(cls, knowledge_id: str, search_mode: str):
        """
        设置知识库的检索模式

        Args:
            knowledge_id: 知识库ID
            search_mode: 检索模式（'traditional' 或 'page_index'）
        """
        from knowledge.models import Knowledge
        from django.db.models import QuerySet

        knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
        if knowledge:
            if 'meta' not in knowledge.meta or knowledge.meta is None:
                knowledge.meta = {}

            knowledge.meta['search_mode'] = search_mode
            knowledge.save()

    @classmethod
    def get_page_index_config(cls, knowledge_meta: Dict) -> Dict:
        """
        获取知识库的PageIndex配置

        Args:
            knowledge_meta: 知识库的meta字典

        Returns:
            PageIndex配置字典
        """
        search_mode = cls.get_search_mode(knowledge_meta)

        if search_mode == cls.SEARCH_MODE_PAGE_INDEX:
            # 返回PageIndex的默认配置
            return {
                'use_tree_filter': knowledge_meta.get('use_tree_filter', cls.DEFAULT_CONFIG['use_tree_filter']),
                'search_mode': knowledge_meta.get('page_index_search_mode', cls.DEFAULT_CONFIG['search_mode']),
                'top_n': knowledge_meta.get('page_index_top_n', cls.DEFAULT_CONFIG['top_n']),
                'similarity_threshold': knowledge_meta.get('page_index_similarity_threshold', cls.DEFAULT_CONFIG['similarity_threshold']),
            }
        else:
            return {}

    @classmethod
    def update_page_index_config(cls, knowledge_id: str, config: Dict):
        """
        更新知识库的PageIndex配置

        Args:
            knowledge_id: 知识库ID
            config: PageIndex配置字典
        """
        from knowledge.models import Knowledge
        from django.db.models import QuerySet

        knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
        if knowledge:
            if 'meta' not in knowledge.meta or knowledge.meta is None:
                knowledge.meta = {}

            # 更新PageIndex配置
            for key, value in config.items():
                knowledge.meta[f'page_index_{key}'] = value

            knowledge.save()

    @classmethod
    def reset_to_traditional(cls, knowledge_id: str):
        """
        将知识库重置为传统检索模式

        Args:
            knowledge_id: 知识库ID
        """
        cls.set_search_mode(knowledge_id, cls.SEARCH_MODE_TRADITIONAL)

    @classmethod
    def reset_to_page_index(cls, knowledge_id: str):
        """
        将知识库设置为PageIndex检索模式

        Args:
            knowledge_id: 知识库ID
        """
        cls.set_search_mode(knowledge_id, cls.SEARCH_MODE_PAGE_INDEX)
