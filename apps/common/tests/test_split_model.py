"""Heading boundaries use matched positions, including repeated heading text."""

from django.test import SimpleTestCase

from common.utils.split_model import SplitModel, get_split_model


class MarkdownHeadingBoundaryTests(SimpleTestCase):
    def split(self, text, **options):
        return [
            {"title": row["title"].strip(), "content": row["content"].strip()}
            for row in get_split_model("guide.md", **options).parse(text)
        ]

    def test_top_level_heading_does_not_match_same_named_table_of_contents_entry(self):
        source = (
            "\r\n# 指南目录\r\n\r\n## 产品介绍\r\n- 使用说明\r\n"
            "\r\n## 附录\r\n附录正文\r\n\r\n# 产品介绍\r\n\r\n## 使用说明\r\n操作正文"
        )
        self.assertEqual(
            self.split(source),
            [
                {"title": "指南目录  产品介绍", "content": "- 使用说明"},
                {"title": "指南目录  附录", "content": "附录正文"},
                {"title": "产品介绍  使用说明", "content": "操作正文"},
            ],
        )

    def test_inline_heading_text_does_not_end_the_previous_section(self):
        self.assertEqual(
            self.split("# 第一章\n正文引用 # 第二章，但仍属于第一章。\n# 第二章\n第二章正文"),
            [
                {"title": "第一章", "content": "正文引用 # 第二章，但仍属于第一章。"},
                {"title": "第二章", "content": "第二章正文"},
            ],
        )

    def test_matching_heading_inside_code_block_does_not_move_real_heading(self):
        code = "```markdown\n# 第二章\n示例代码\n```"
        self.assertEqual(
            self.split(f"# 第一章\n{code}\n# 第二章\n第二章正文"),
            [{"title": "第一章", "content": code}, {"title": "第二章", "content": "第二章正文"}],
        )

    def test_repeated_headings_keep_their_own_bodies(self):
        self.assertEqual(
            self.split("# 同名章节\n第一段\n# 同名章节\n第二段"),
            [{"title": "同名章节", "content": "第一段"}, {"title": "同名章节", "content": "第二段"}],
        )

    def test_preamble_and_nested_introductions_keep_source_order_without_duplicates(self):
        self.assertEqual(
            self.split("引言\n# 章节\n章节导语\n## 小节\n小节导语\n### 细节\n详细内容"),
            [
                {"title": "", "content": "引言"},
                {"title": "章节", "content": "章节导语"},
                {"title": "章节  小节", "content": "小节导语"},
                {"title": "章节  小节  细节", "content": "详细内容"},
            ],
        )

    def test_long_heading_tail_is_preserved_and_paragraph_limit_still_applies(self):
        heading = "长" * 300
        result = self.split(f"# {heading}\n" + "文" * 120, limit=50)
        self.assertTrue(all(len(row["title"]) <= 255 and len(row["content"]) <= 50 for row in result))
        self.assertEqual(result[0]["title"] + "".join(row["content"] for row in result), heading + "\n" + "文" * 120)

    def test_custom_capture_patterns_use_the_matched_group_position(self):
        result = SplitModel([r"(?m)^Section: (.+)$"], with_filter=False).parse(
            "Heading appears in this introduction.\nSection: Heading\nBody"
        )
        self.assertEqual(result[-1]["title"].strip(), "Heading")
        self.assertEqual(result[-1]["content"].strip(), "Body")
        self.assertEqual(
            "".join(row["content"] for row in result[:-1]).strip(), "Heading appears in this introduction.\nSection:"
        )

    def test_invalid_or_empty_patterns_leave_plain_text_intact(self):
        for pattern in (None, "", " ", "["):
            with self.subTest(pattern=pattern):
                self.assertEqual(
                    SplitModel([pattern], with_filter=False).parse("正文"), [{"title": "", "content": "正文"}]
                )
