from django.test import SimpleTestCase

from common.utils.common import markdown_to_plain_text


class MarkdownToPlainTextTestCase(SimpleTestCase):
    def test_removes_embedded_markup_contents(self):
        cases = {
            'before <audio src="clip.mp3">audio fallback</audio> after': "before after",
            'before <video src="clip.mp4">video fallback</video> after': "before after",
            'before <form_rander>{"label":"private"}</form_rander> after': "before after",
        }

        for markup, expected in cases.items():
            with self.subTest(markup=markup):
                self.assertEqual(markdown_to_plain_text(markup), expected)


class SmartSplitParagraphTestCase(SimpleTestCase):
    """smart_split_paragraph must treat the full-width exclamation/question marks
    as split points just like their ASCII counterparts (the list is documented as
    中英文感叹号/问号)."""

    def test_splits_at_full_width_exclamation_and_question_marks(self):
        from common.utils.split_model import smart_split_paragraph
        for mark in ('！', '？'):
            with self.subTest(mark=mark):
                text = '内' * 60 + mark + '容' * 200
                parts = smart_split_paragraph(text, 100)
                self.assertEqual(len(parts[0]), 61)
                self.assertTrue(parts[0].endswith(mark))
                self.assertEqual(''.join(parts), text)

    def test_ascii_and_period_split_points_still_work(self):
        from common.utils.split_model import smart_split_paragraph
        for mark in ('!', '?', '.', '。'):
            with self.subTest(mark=mark):
                text = 'x' * 60 + mark + 'y' * 200
                parts = smart_split_paragraph(text, 100)
                self.assertEqual(len(parts[0]), 61)
                self.assertTrue(parts[0].endswith(mark))
                self.assertEqual(''.join(parts), text)

    def test_hard_cut_when_no_split_point_in_window(self):
        from common.utils.split_model import smart_split_paragraph
        parts = smart_split_paragraph('z' * 250, 100)
        self.assertEqual([len(part) for part in parts], [100, 100, 50])
