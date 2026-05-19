# apps/common/locale/config_helper.py
"""
语言配置助手
为 Config 类提供语言相关的辅助方法
"""

import os
from typing import List, Tuple, Dict

from common.utils.logger import maxkb_logger as logger


class LocaleConfigHelper:
    """语言配置助手 - 供 Config 类使用"""

    # 标准化语言代码到显示名称的映射（ISO 639-1 标准）
    STANDARD_LANGUAGE_NAMES = {
        "en": "English",
        "en-US": "English",
        "zh-CN": "中文简体",
        "zh-Hant": "中文繁体",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "it": "Italiano",
        "pt": "Português",
        "pt-br": "Português (Brasil)",
        "ru": "Русский",
        "ar": "العربية",
        "hi": "हिन्दी",
        "th": "ไทย",
        "vi": "Tiếng Việt",
        "id": "Bahasa Indonesia",
        "ms": "Bahasa Melayu",
        "tr": "Türkçe",
        "nl": "Nederlands",
        "pl": "Polski",
        "sv": "Svenska",
        "da": "Dansk",
        "fi": "Suomi",
        "no": "Norsk",
        "cs": "Čeština",
        "hu": "Magyar",
        "ro": "Română",
        "uk": "Українська",
        "el": "Ελληνικά",
        "he": "עברית",
        "fa": "فارسی",
        "ur": "اردو",
        "bn": "বাংলা",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "mr": "मराठी",
    }

    DEFAULT_LANGUAGES = [("en", "English"), ("zh", "中文简体"), ("zh-hant", "中文繁体")]

    @staticmethod
    def get_languages(config_object, project_dir: str) -> List[Tuple[str, str]]:
        """
        获取支持的语言列表（带缓存）

        Args:
            config_object: Config 实例
            project_dir: 项目根目录

        Returns:
            语言列表 [(code, name), ...]
        """
        from .cache import get_locale_cache

        cache = get_locale_cache()

        # 尝试从缓存获取
        cached_languages = cache.get()
        if cached_languages is not None:
            logger.debug("Using cached languages list")
            return cached_languages

        # 部署外置语言包
        from .manager import deploy_external_locales

        deploy_external_locales()

        # 获取用户自定义的语言名称映射
        custom_languages = LocaleConfigHelper._parse_custom_languages(config_object.get("LANGUAGES", ""))

        # 扫描语言包目录
        all_languages = {}
        internal_locales_dir = os.path.join(project_dir, "apps", "locales")

        if os.path.isdir(internal_locales_dir):
            LocaleConfigHelper._scan_locale_directory(
                internal_locales_dir, all_languages, LocaleConfigHelper.STANDARD_LANGUAGE_NAMES, custom_languages
            )

        # 如果没有检测到任何语言，返回默认语言
        if not all_languages:
            languages = LocaleConfigHelper.DEFAULT_LANGUAGES
        else:
            # 按语言代码排序并转换为列表
            languages = [(code, name) for code, name in sorted(all_languages.items())]

        # 缓存结果
        cache.set(languages)
        logger.info(f"Detected {len(languages)} languages, cached for 5 minutes")

        return languages

    @staticmethod
    def _parse_custom_languages(languages_str: str) -> Dict[str, str]:
        """
        解析用户自定义的语言名称映射

        Args:
            languages_str: LANGUAGES 配置字符串，格式如 "ja:日本語,ko:한국어"

        Returns:
            自定义语言映射字典
        """
        custom_languages = {}
        if not languages_str:
            return custom_languages

        for lang_pair in languages_str.split(","):
            lang_pair = lang_pair.strip()
            if ":" in lang_pair:
                code, name = lang_pair.split(":", 1)
                custom_languages[code.strip()] = name.strip()

        return custom_languages

    @staticmethod
    def _scan_locale_directory(
        locales_dir: str,
        languages_dict: Dict[str, str],
        standard_names: Dict[str, str],
        custom_languages: Dict[str, str],
    ):
        """
        扫描指定目录下的语言包

        Args:
            locales_dir: 语言包目录路径
            languages_dict: 存储检测到的语言的字典（会被修改）
            standard_names: 标准语言名称映射
            custom_languages: 自定义语言名称映射
        """
        if not os.path.isdir(locales_dir):
            return

        for lang_dir in os.listdir(locales_dir):
            lang_path = os.path.join(locales_dir, lang_dir)
            if os.path.isdir(lang_path):
                # 将目录名转换为标准语言代码格式 (zh_CN -> zh-cn, en_US -> en-us)
                lang_code = lang_dir.replace("_", "-")

                # 获取显示名称（优先级：自定义 > 标准映射 > 目录名）
                display_name = None
                if lang_code in custom_languages:
                    display_name = custom_languages[lang_code]
                elif lang_code in standard_names:
                    display_name = standard_names[lang_code]
                else:
                    # 尝试匹配基础代码（如 ja-JP -> ja）
                    base_code = lang_code.split("-")[0]
                    if base_code in custom_languages:
                        display_name = custom_languages[base_code]
                    elif base_code in standard_names:
                        display_name = standard_names[base_code]
                    else:
                        display_name = lang_dir

                # 同时注册完整代码和基础代码，实现前后端兼容
                # 例如：目录名为 ja_JP，会同时注册 'ja-jp' 和 'ja'
                languages_dict[lang_code] = display_name

                # 如果语言代码包含地区信息，同时注册基础代码
                if "-" in lang_code:
                    base_code = lang_code.split("-")[0]
                    # 只有当基础代码还没有被注册时，才注册它
                    if base_code not in languages_dict:
                        languages_dict[base_code] = display_name

    @staticmethod
    def invalidate_cache():
        """清除语言缓存（当语言包更新时调用）"""
        from .cache import get_locale_cache

        get_locale_cache().invalidate()
        logger.info("Language cache invalidated")
