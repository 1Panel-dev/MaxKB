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
