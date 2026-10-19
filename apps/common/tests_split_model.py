import re
import unittest
from types import SimpleNamespace

from common.handle.impl.text.text_split_handle import TextSplitHandle
from common.utils.split_model import SplitModel, get_split_model


class SplitModelTestCase(unittest.TestCase):
    @staticmethod
    def paragraphs(text, filename='test.md'):
        return [
            (' '.join(row['title'].split()), row['content'].strip())
            for row in get_split_model(filename).parse(text)
        ]

    def test_same_heading_at_different_levels(self):
        for level in range(1, 6):
            with self.subTest(level=level):
                parent, child = '#' * level, '#' * (level + 1)
                text = (
                    f'{parent} 员工手册目录\n\n'
                    f'{child} 第一部分：公司概述\n目录条目一\n\n'
                    f'{child} 第二部分：人力资源\n目录条目二\n\n'
                    f'{parent} 第一部分：公司概述\n正文内容\n'
                )
                self.assertEqual(self.paragraphs(text), [
                    ('员工手册目录 第一部分：公司概述', '目录条目一'),
                    ('员工手册目录 第二部分：人力资源', '目录条目二'),
                    ('第一部分：公司概述', '正文内容'),
                ])

    def test_heading_text_in_body_does_not_start_section(self):
        text = '# 目录\n引用：# 正文\n\n# 正文\n正文内容'
        self.assertEqual(self.paragraphs(text), [
            ('目录', '引用：# 正文'),
            ('正文', '正文内容'),
        ])

    def test_heading_text_in_code_block_does_not_start_section(self):
        text = '# 目录\n```markdown\n# 正文\n```\n\n# 正文\n正文内容'
        self.assertEqual(self.paragraphs(text), [
            ('目录', '```markdown\n# 正文\n```'),
            ('正文', '正文内容'),
        ])

    def test_repeated_headings_keep_each_body(self):
        text = '# 章节\n第一段提到 # 章节\n\n# 章节\n第二段'
        self.assertEqual(self.paragraphs(text), [
            ('章节', '第一段提到 # 章节'),
            ('章节', '第二段'),
        ])

    def test_heading_prefix_does_not_end_section(self):
        text = '# 前言\n引用：# 公司概述扩展\n\n# 公司概述扩展\n扩展内容\n\n# 公司概述\n正文'
        self.assertEqual(self.paragraphs(text), [
            ('前言', '引用：# 公司概述扩展'),
            ('公司概述扩展', '扩展内容'),
            ('公司概述', '正文'),
        ])

    def test_preamble_is_preserved(self):
        text = '前言提到 # 正文\n\n# 正文\n正文内容'
        self.assertEqual(self.paragraphs(text), [
            ('', '前言提到 # 正文'),
            ('正文', '正文内容'),
        ])

    def test_custom_patterns_with_capture_groups(self):
        pattern = re.compile(r'(?m)^(# .+)$|^(## .+)$')
        text = '# 目录\n引用：## 公司概述\n\n## 公司概述\n正文'
        result = SplitModel([pattern], with_filter=False).parse(text)
        self.assertEqual([(row['title'].strip(), row['content'].strip()) for row in result], [
            ('目录', '引用：## 公司概述'),
            ('公司概述', '正文'),
        ])

    def test_invalid_patterns_fall_back_to_plain_text(self):
        for pattern in (None, '', '   ', '['):
            with self.subTest(pattern=pattern):
                self.assertEqual(SplitModel([pattern]).parse('普通文本'), [
                    {'title': '', 'content': '普通文本'},
                ])

    def test_long_heading_keeps_text_after_title_limit(self):
        heading = '# ' + '标题' * 150
        rows = get_split_model('test.md').parse(heading + '\n正文')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['title'], heading[:255].replace('#', ''))
        self.assertEqual(rows[0]['content'], heading[255:] + '\n正文')

    def test_plain_text_splitting(self):
        self.assertEqual(self.paragraphs('第一段\n\n第二段', 'test.txt'), [
            ('', '第一段'),
            ('', '第二段'),
        ])

    def test_text_upload_handler_keeps_directory_under_its_heading(self):
        text = (
            '# 员工手册目录\n\n'
            '## 第一部分：公司概述\n目录条目一\n\n'
            '## 第二部分：人力资源\n目录条目二\n\n'
            '# 第一部分：公司概述\n\n'
            '## 公司简介\n正文内容\n'
        )
        for newline in ('\n', '\r\n', '\r'):
            with self.subTest(newline=repr(newline)):
                result = TextSplitHandle().handle(
                    SimpleNamespace(name='员工手册目录.md'), [], False, 100000,
                    lambda _: text.replace('\n', newline).encode('utf-8'), None,
                )
                self.assertEqual([
                    (' '.join(row['title'].split()), row['content'].strip()) for row in result['content']
                ], [
                    ('员工手册目录 第一部分：公司概述', '目录条目一'),
                    ('员工手册目录 第二部分：人力资源', '目录条目二'),
                    ('第一部分：公司概述 公司简介', '正文内容'),
                ])


if __name__ == '__main__':
    unittest.main()
