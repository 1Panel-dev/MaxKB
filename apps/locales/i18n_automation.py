# coding=utf-8
"""
Django 国际化翻译文件自动化脚本
功能：
1. 缓存已翻译的内容
2. 扫描所有Python文件中的国际化代码
3. 合并已有翻译和新发现的内容
4. 生成排序后的翻译文件
"""

import re
from pathlib import Path
from typing import Dict


# 配置1：需要扫描的语言
LANGUAGES = ['en_US', 'zh_CN', 'zh_Hant']

# 配置2：是否保留无代码来源(遗留)的项？
# 说明：如果想从 django.po 文件中清除它们，请将此属性设置为 False
# 注意：为 False 时，保险起见，保留已翻译项
KEEP_NO_SOURCE = True

# 配置3：是否保留翻译与原文一样的翻译内容？
# 说明：默认：不保留，因为与原文一样没必要保留。
# 例：为False时：
#   ```text
#   msgid "xxx"
#   msgstr "xxx"
#   ```
#   会被简化为
#   ```text
#   msgid "xxx"
#   msgstr ""
#   ```
KEEP_SAME_TRANSLATION = False

# 配置4：是否备份原 django.po 文件。
# 说明：因为有VCS，所以默认不备份。
BACKUP_PO = False


class I18nAutomation:
    """国际化自动化工具类"""

    def __init__(self, base_dir: str):
        """
        初始化工具

        Args:
            base_dir: 项目根目录路径
        """
        self.base_dir = Path(base_dir)
        self.locales_dir = self.base_dir / 'apps' / 'locales'

        # 翻译数据存储格式: { "原文": {"zh_CN": "翻译", "zh_Hant": "翻译", "from_sources": [...] } }
        self.translations = {}

    def parse_po_file(self, po_file_path: Path) -> Dict[str, str]:
        """
        解析 .po 文件，提取 msgid 和 msgstr 的映射关系

        Args:
            po_file_path: .po 文件路径

        Returns:
            {msgid: msgstr} 字典
        """
        translations = {}

        if not po_file_path.exists():
            print(f"警告: 文件不存在 - {po_file_path}")
            return translations

        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用更完善的解析逻辑处理多行 msgid/msgstr
        # 先找到所有的 msgid/msgstr 块
        entries = self._extract_po_entries(content)

        for msgid, msgstr in entries.items():
            # 跳过空字符串
            if msgid and msgid.strip():
                # 处理转义字符
                msgid_unescaped = self._unescape_string(msgid)
                msgstr_unescaped = self._unescape_string(msgstr)

                if msgstr_unescaped:
                    # 当 配置 KEEP_SAME_TRANSLATION 为 True 或 翻译内容与原文不一致，则保留
                    if KEEP_SAME_TRANSLATION or msgstr_unescaped != msgid_unescaped:
                        translations[msgid_unescaped] = msgstr_unescaped

        return translations

    def _extract_po_entries(self, content: str) -> Dict[str, str]:
        """
        从 .po 文件内容中提取 msgid 和 msgstr 对
        支持多行字符串格式

        Args:
            content: .po 文件内容

        Returns:
            {msgid: msgstr} 字典
        """
        entries = {}
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 查找 msgid 开始
            if line.startswith('msgid '):
                # 提取 msgid 的所有行
                msgid_parts = []
                msgid_line = line[6:].strip()  # 去掉 'msgid '

                # 如果第一行有内容（可能是 msgid "" 或 msgid "..."）
                if msgid_line:
                    msgid_parts.append(msgid_line)

                # 继续读取后续的行（以 " 开头的 continuation lines）
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    # 如果下一行以 " 开头，说明是多行字符串的延续
                    if next_line.startswith('"'):
                        msgid_parts.append(next_line)
                        i += 1
                    # 如果遇到 msgstr，停止读取 msgid
                    elif next_line.startswith('msgstr '):
                        break
                    # 跳过空行和注释，继续寻找 msgstr
                    elif next_line == '' or next_line.startswith('#'):
                        i += 1
                        continue
                    # 其他情况也停止
                    else:
                        print(f"其他情况也停止: {next_line}")
                        break

                # 现在查找 msgstr（跳过中间的空行和注释）
                msgstr_parts = []
                while i < len(lines):
                    current_line = lines[i].strip()
                    if current_line.startswith('msgstr '):
                        msgstr_line = current_line[7:].strip()  # 去掉 'msgstr '
                        if msgstr_line:
                            msgstr_parts.append(msgstr_line)
                        i += 1
                        break
                    # 跳过空行和注释，继续寻找 msgstr
                    elif current_line == '' or current_line.startswith('#'):
                        i += 1
                        continue
                    else:
                        # 遇到其他内容，说明没有 msgstr
                        i += 1
                        print(f"遇到其他内容，说明没有 msgstr: {current_line}")
                        break

                # 如果找到了 msgstr，继续读取其后续行
                if msgstr_parts:
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('"'):
                            msgstr_parts.append(next_line)
                            i += 1
                        else:
                            break

                # 合并多行字符串
                if msgid_parts and msgstr_parts:
                    msgid = self._join_multiline_string(msgid_parts)
                    msgstr = self._join_multiline_string(msgstr_parts)
                    entries[msgid] = msgstr
            else:
                i += 1

        return entries

    def _join_multiline_string(self, parts: list) -> str:
        """
        将多行字符串部分合并为一个字符串
        例如: ['"第一部分"', '"第二部分"'] -> "第一部分第二部分"

        Args:
            parts: 字符串部分列表

        Returns:
            合并后的字符串
        """
        if not parts:
            return ''

        # 移除每个部分的引号并拼接
        result = ''
        for part in parts:
            # 去除首尾的引号和空格
            cleaned = part.strip().strip('"')
            result += cleaned

        return result

    def _unescape_string(self, s: str) -> str:
        """
        处理转义字符串

        Args:
            s: 原始字符串

        Returns:
            处理后的字符串
        """
        # 处理常见的转义字符
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\"', '"')
        s = s.replace('\\\\', '\\')
        return s

    def _escape_string(self, s: str) -> str:
        """
        转义字符串用于写入 .po 文件

        Args:
            s: 原始字符串

        Returns:
            转义后的字符串
        """
        s = s.replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        return s

    def cache_existing_translations(self):
        """
        步骤1: 缓存 en_US、zh_CN 和 zh_Hant 中已翻译的内容
        格式: { "原文": {"en_US": "翻译内容", "zh_CN": "翻译内容", "zh_Hant": "翻译内容"} }
        """
        print("\n" + "="*60)
        print("步骤1: 缓存已有的翻译内容")
        print("="*60)

        cached = {}

        for lang in LANGUAGES:
            po_file = self.locales_dir / lang / 'LC_MESSAGES' / 'django.po'
            lang_translations = self.parse_po_file(po_file)
            print(f"从 django.po 解析到 {len(lang_translations)} 条翻译（{lang}）")

            for msgid, msgstr in lang_translations.items():
                if msgid not in cached:
                    cached[msgid] = {}
                cached[msgid][lang] = msgstr

        self.cached_translations = cached
        print(f"共缓存 {len(cached)} 条已有翻译")
        return cached

    def extract_i18n_from_python_files(self) -> Dict[str, dict]:
        """
        步骤2: 读取所有 *.py 文件中的国际化代码
        格式: _("原文内容")

        Returns:
            { "原文": {"en_US": "", "zh_CN": "", "zh_Hant": "", "from_sources": [...]} }
        """
        print("\n" + "="*60)
        print("步骤2: 扫描 Python 文件中的国际化代码")
        print("="*60)

        i18n_strings = {}
        apps_dir = self.base_dir / 'apps'

        # 匹配各种国际化字符串模式：
        # 1. _("xxx" "yyy") 或 _('xxx' 'yyy') - 括号内多字符串拼接
        # 2. _("""...""") 或 _('''...''') - 三引号多行字符串
        # 3. _("...") 或 _('...') - 单行字符串
        patterns = [
            # 1. 匹配括号内多个字符串拼接 _("str1" "str2") 或 _("str1" 'str2') 等混合形式
            re.compile(
                r'\b(?:_|gettext_lazy|gettext)\(\s*'
                r'(?:r?(?:"(?:[^"\\]|\\.)+"|\'(?:[^\'\\]|\\.)+\')\s*){2,}'
                r'\)',
                re.MULTILINE | re.DOTALL
            ),
            # 2. 匹配三引号双引号 _("""...""")
            re.compile(r'\b(?:_|gettext_lazy|gettext)\(\s*r?"""((?:[^"\\]|\\.|"(?!"")|\n)*?)"""\s*\)', re.MULTILINE | re.DOTALL),
            # 2. 匹配三引号单引号 _('''...''')
            re.compile(r"\b(?:_|gettext_lazy|gettext)\(\s*r?'''((?:[^'\\]|\\.|'(?!'')|\n)*?)'''\s*\)", re.MULTILINE | re.DOTALL),
            # 3. 匹配单行双引号 _("...")
            re.compile(r'\b(?:_|gettext_lazy|gettext)\(\s*r?"((?:[^"\\]|\\.)+?)"\s*\)', re.MULTILINE | re.DOTALL),
            # 3. 匹配单行单引号 _('...')
            re.compile(r"\b(?:_|gettext_lazy|gettext)\(\s*r?'((?:[^'\\]|\\.)+?)'\s*\)", re.MULTILINE | re.DOTALL),
        ]

        # 递归查找所有 .py 文件
        py_files = list(apps_dir.rglob('*.py'))
        print(f"找到 {len(py_files)} 个 Python 文件")

        scanned_count = 0
        for py_file in py_files:
            # 跳过 __pycache__、migrations 和 locales 目录
            if '__pycache__' in str(py_file) or 'migrations' in str(py_file) or 'locales' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_scanned = False
                for index, pattern in enumerate(patterns):
                    matches = pattern.finditer(content)
                    current_pattern_current_file_line_no_array = []  # 同正则同文件匹配到的代码行号，用于保留同匹配串在同一行匹配到多个时多次显示该行号
                    for match in matches:
                        full_match = match.group(0)

                        # 对于多字符串拼接模式，需要特殊处理提取内容
                        if index == 0:  # 注：必须将该正则放在 patterns 的第一位
                            # 提取括号内所有的字符串并拼接
                            msgid = self._extract_concatenated_strings(full_match)
                        else:
                            # 普通模式，直接提取捕获组
                            msgid = match.group(1) if match.lastindex else None

                        if msgid is None:
                            continue

                        msgid = self._unescape_string(msgid)

                        if msgid and msgid.strip():
                            msgid = msgid.replace("\\'", "'").replace('\\"', '"')
                            if msgid not in i18n_strings:
                                i18n_strings[msgid] = {
                                    'en_US': '',
                                    'zh_CN': '',
                                    'zh_Hant': '',
                                    'from_sources': {}
                                }

                            # 记录来源文件和行号
                            relative_path = str(py_file.relative_to(self.base_dir)).replace("\\", "/")
                            line_no = content[:match.start()].count('\n') + 1

                            if relative_path not in i18n_strings[msgid]['from_sources']:
                                i18n_strings[msgid]['from_sources'][relative_path] = [line_no]
                                current_pattern_current_file_line_no_array.append(line_no)
                                file_scanned = True
                            else:
                                if line_no not in i18n_strings[msgid]['from_sources'][relative_path] or line_no in current_pattern_current_file_line_no_array:
                                    i18n_strings[msgid]['from_sources'][relative_path].append(line_no)
                                    current_pattern_current_file_line_no_array.append(line_no)

                if file_scanned:
                    scanned_count += 1

            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")

        print(f"扫描了 {scanned_count} 个文件")
        print(f"提取到 {len(i18n_strings)} 条国际化字符串")

        self.scanned_i18n = i18n_strings
        return i18n_strings

    def _extract_concatenated_strings(self, match_str: str) -> str:
        """
        从括号内的多个字符串拼接中提取完整内容
        例如: _("Hello" " World") -> "Hello World"

        Args:
            match_str: 完整的匹配字符串，如 _("str1" "str2")

        Returns:
            拼接后的字符串内容
        """
        # 找到第一个 ( 和最后一个 ) 之间的内容
        start = match_str.find('(')
        end = match_str.rfind(')')
        if start == -1 or end == -1:
            return ''

        inner = match_str[start+1:end].strip()

        # 移除开头的 r (原始字符串标记)
        if inner.startswith('r') or inner.startswith('R'):
            inner = inner[1:]

        # 提取所有字符串字面量并拼接
        result = []
        i = 0
        while i < len(inner):
            # 跳过空白
            if inner[i].isspace():
                i += 1
                continue

            # 检测字符串开始
            if inner[i] in ('"', "'"):
                quote_char = inner[i]
                i += 1
                string_chars = []

                # 检查是否是三引号
                if i < len(inner) - 1 and inner[i:i+2] == quote_char * 2:
                    # 三引号
                    i += 2
                    while i < len(inner) - 2:
                        if inner[i:i+3] == quote_char * 3:
                            i += 3
                            break
                        elif inner[i] == '\\' and i + 1 < len(inner):
                            string_chars.append(inner[i:i+2])
                            i += 2
                        else:
                            string_chars.append(inner[i])
                            i += 1
                    else:
                        # 未闭合，跳出
                        break
                else:
                    # 单引号
                    while i < len(inner):
                        if inner[i] == quote_char:
                            i += 1
                            break
                        elif inner[i] == '\\' and i + 1 < len(inner):
                            string_chars.append(inner[i:i+2])
                            i += 2
                        else:
                            string_chars.append(inner[i])
                            i += 1

                result.append(''.join(string_chars))
            else:
                i += 1

        return ''.join(result)

    def merge_translations(self):
        """
        步骤3: 将缓存的翻译内容覆盖到新数据中
        """
        print("\n" + "="*60)
        print("步骤3: 合并已有翻译")
        print("="*60)

        # 以扫描到的国际化字符串为基础
        merged = dict(self.scanned_i18n)

        # 将缓存的翻译覆盖进去
        for msgid, translations in self.cached_translations.items():
            if msgid in merged:
                # 如果该字符串在代码中存在，更新翻译
                for lang in LANGUAGES:
                    if lang in translations:
                        merged[msgid][lang] = translations[lang]
            else:
                # 如果该字符串在代码中不存在，但仍然保留（可能是遗留的翻译）
                merged[msgid] = {
                    'en_US': translations.get('en_US', ''),
                    'zh_CN': translations.get('zh_CN', ''),
                    'zh_Hant': translations.get('zh_Hant', ''),
                    'from_sources': {}
                }

        self.merged_translations = merged
        print(f"合并完成，共 {len(merged)} 条翻译项")
        print(f"其中有翻译内容的: {sum(1 for v in merged.values() if v['en_US'] or v['zh_CN'] or v['zh_Hant'])}")

        return merged

    def generate_po_file_content(self, lang: str, translations: Dict) -> str:
        """
        生成 .po 文件内容

        Args:
            lang: 语言代码 (zh_CN, zh_Hant, en_US)
            translations: 翻译数据字典

        Returns:
            .po 文件内容字符串
        """
        lines = []

        # 文件头
        header = '''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-06-18 17:33+0800\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''
        lines.append(header)

        # 按原文排序：移除前面的空白符并转大写后排序
        sorted_keys = sorted(translations.keys(), key=lambda x: re.sub(r'^\s+', '', x).upper())

        for msgid in sorted_keys:
            data = translations[msgid]

            # 获取该语言的翻译
            msgstr = data.get(lang, '')

            # 获取来源信息
            from_sources = data.get('from_sources')

            # 无代码来源(遗留)的，说明后端源码中已经移除，所以从 django.po 文件中移除（保险起见，保留已翻译项）
            if not KEEP_NO_SOURCE and not from_sources and not msgstr:
                continue

            if from_sources:
                # 分组显示
                for relative_path, line_no_list in sorted(from_sources.items()):
                    line_no_list.sort()
                    for line_no in line_no_list:
                        lines.append(f"#: {relative_path}:{line_no}")
            else:
                lines.append("#: no source")

            # 添加 msgid 和 msgstr
            escaped_msgid = self._escape_string(msgid)
            escaped_msgstr = self._escape_string(msgstr)

            lines.append(f'msgid "{escaped_msgid}"')
            lines.append(f'msgstr "{escaped_msgstr}"')
            lines.append('')  # 空行分隔

        return '\n'.join(lines)

    def write_po_files(self):
        """
        步骤4: 将数据按原文排序，分别写入三个翻译文件
        """
        print("\n" + "="*60)
        print("步骤4: 生成翻译文件")
        print("="*60)

        for lang in LANGUAGES:
            po_file_path = self.locales_dir / lang / 'LC_MESSAGES' / 'django.po'

            # 生成文件内容
            content = self.generate_po_file_content(lang, self.merged_translations)

            # 备份原文件
            if BACKUP_PO:
                backup_path = po_file_path.with_suffix('.po.bak')
                if po_file_path.exists():
                    import shutil
                    shutil.copy2(po_file_path, backup_path)
                    print(f"已备份原文件: {backup_path}")

            # 写入新文件
            with open(po_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 统计信息
            translated_count = sum(1 for v in self.merged_translations.values()
                                   if v.get(lang, ''))
            total_count = len(self.merged_translations)

            print(f"{lang}:{'  ' if len(lang) < 7 else ''} 共 {total_count} 条，已翻译 {translated_count} 条")

        print("\n所有翻译文件已生成完成！！！")

    def generate_report(self):
        """
        生成翻译报告
        """
        print("\n\n" + "="*60)
        print("翻译统计报告")
        print("="*60)

        total = len(self.merged_translations)
        en_us_translated = sum(1 for v in self.merged_translations.values() if v['en_US'])
        zh_cn_translated = sum(1 for v in self.merged_translations.values() if v['zh_CN'])
        zh_hant_translated = sum(1 for v in self.merged_translations.values() if v['zh_Hant'])
        has_source = sum(1 for v in self.merged_translations.values() if v['from_sources'])
        no_source = total - has_source

        print(f"\n总翻译条目数: {total}")
        print(f"英文已翻译: {en_us_translated} ({en_us_translated/total*100:.2f}%)")
        print(f"简体中文已翻译: {zh_cn_translated} ({zh_cn_translated/total*100:.2f}%)")
        print(f"繁体中文已翻译: {zh_hant_translated} ({zh_hant_translated/total*100:.2f}%)")
        print(f"有代码来源: {has_source}")
        print(f"无代码来源(遗留): {no_source} （可将脚本中的 `KEEP_NO_SOURCE = False` 来自动清除这些项）")

        # 找出未翻译的项目示例
        print("\n\n" + "="*60)
        print("前10个未翻译简体中文的项目:")
        print("="*60)
        count = 0
        for msgid, data in self.merged_translations.items():
            if not data['zh_CN'] and count < 10:
                print(f"- {msgid[:80]}{'...' if len(msgid) > 80 else ''}")
                count += 1

        # 打印简体翻译但繁体未翻译，或繁体翻译但简体未翻译的项
        print("\n" + "="*60)
        print("不一致翻译项（简体已翻译但繁体未翻译，或繁体已翻译但简体未翻译）:")
        print("="*60)

        simplified_only = []  # 简体已翻译但繁体未翻译
        traditional_only = []  # 繁体已翻译但简体未翻译

        for msgid, data in self.merged_translations.items():
            has_zh_cn = bool(data['zh_CN'])
            has_zh_hant = bool(data['zh_Hant'])

            if has_zh_cn and not has_zh_hant:
                simplified_only.append(msgid)
            elif has_zh_hant and not has_zh_cn:
                traditional_only.append(msgid)

        if simplified_only:
            print(f"简体已翻译但繁体未翻译 ({len(simplified_only)} 项):")
            for i, msgid in enumerate(simplified_only[:20], 1):
                preview = msgid[:80] + '...' if len(msgid) > 80 else msgid
                translation = self.merged_translations[msgid]['zh_CN']
                trans_preview = translation[:50] + '...' if len(translation) > 50 else translation
                print(f"  {i}. 原文: {preview}")
                print(f"     简体: {trans_preview}")

            if len(simplified_only) > 20:
                print(f"  ... 还有 {len(simplified_only) - 20} 项")

        if traditional_only:
            if simplified_only:
                print("")  # 换行
            print(f"繁体已翻译但简体未翻译 ({len(traditional_only)} 项):")
            for i, msgid in enumerate(traditional_only[:20], 1):
                preview = msgid[:80] + '...' if len(msgid) > 80 else msgid
                translation = self.merged_translations[msgid]['zh_Hant']
                trans_preview = translation[:50] + '...' if len(translation) > 50 else translation
                print(f"  {i}. 原文: {preview}")
                print(f"     繁体: {trans_preview}")

            if len(traditional_only) > 20:
                print(f"  ... 还有 {len(traditional_only) - 20} 项")

        if not simplified_only and not traditional_only:
            print("\n无不一致翻译项 ✓")

    def run(self):
        """
        执行完整流程
        """
        print("开始 Django 国际化翻译文件自动化处理")
        print(f"项目根目录: {self.base_dir}")

        # 步骤1: 缓存已有翻译
        self.cache_existing_translations()

        # 步骤2: 扫描 Python 文件
        self.extract_i18n_from_python_files()

        # 步骤3: 合并翻译
        self.merge_translations()

        # 步骤4: 写入文件
        self.write_po_files()

        # 生成报告
        self.generate_report()

        print("\n" + "="*60)
        print("处理完成！")
        print("="*60)


def main():
    """主函数"""
    # 获取当前脚本所在的项目根目录
    # 假设脚本在项目根目录下运行
    base_dir = Path(__file__).parent.parent.parent

    # 或者可以手动指定
    # base_dir = Path(r'E:\Workspace_Java\3rd-party\1Panel-dev\MaxKB')

    print(f"使用项目根目录: {base_dir}")

    # 创建工具实例并运行
    tool = I18nAutomation(str(base_dir))
    tool.run()


if __name__ == '__main__':
    main()
