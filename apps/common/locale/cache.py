# apps/common/locale/cache.py
"""
语言配置缓存管理
避免重复扫描文件系统，提升性能
"""

import time
from typing import Optional, List, Tuple


class LocaleCache:
    """语言配置缓存"""

    def __init__(self, ttl: int = 300):
        """
        初始化缓存

        Args:
            ttl: 缓存有效期（秒），默认 5 分钟
        """
        self._cache: Optional[List[Tuple[str, str]]] = None
        self._timestamp: float = 0
        self._ttl = ttl

    def get(self) -> Optional[List[Tuple[str, str]]]:
        """获取缓存的语言列表"""
        if self._cache is not None and (time.time() - self._timestamp) < self._ttl:
            return self._cache
        return None

    def set(self, languages: List[Tuple[str, str]]):
        """设置缓存的语言列表"""
        self._cache = languages
        self._timestamp = time.time()

    def invalidate(self):
        """清除缓存"""
        self._cache = None
        self._timestamp = 0

    @property
    def is_valid(self) -> bool:
        """检查缓存是否有效"""
        return self._cache is not None and (time.time() - self._timestamp) < self._ttl


# 全局缓存实例
_locale_cache = LocaleCache(ttl=300)


def get_locale_cache() -> LocaleCache:
    """获取全局语言缓存实例"""
    return _locale_cache
