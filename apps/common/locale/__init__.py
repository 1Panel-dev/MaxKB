# apps/common/locale/__init__.py
"""
语言管理公共模块
提供跨项目共享的语言配置和部署功能
"""

from .manager import LocaleManager, get_locale_manager, deploy_external_locales
from .config_helper import LocaleConfigHelper

__all__ = [
    'LocaleManager',
    'get_locale_manager',
    'deploy_external_locales',
    'LocaleConfigHelper'
]
