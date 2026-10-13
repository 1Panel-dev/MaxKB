import csv
import io

from django.test import SimpleTestCase

from common.handle.impl.table.csv_parse_table_handle import CsvParseTableHandle
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


class CsvParseTableHandleTestCase(SimpleTestCase):
    """Table-mode CSV import must honor RFC 4180 quoting exactly like the QA/split
    handles and get_content() of the same family already do (they all use csv.reader)."""

    @staticmethod
    def _parse(csv_text):
        class _File:
            name = 'test.csv'

            def read(self):
                return csv_text.encode('utf-8')

        return CsvParseTableHandle().handle(_File(), lambda file: file.read(), lambda images: None)

    def test_quoted_field_with_comma_stays_one_value(self):
        paragraphs = self._parse('name,city\n"Smith, John",NY\n')[0]['paragraphs']
        self.assertEqual(paragraphs, [{'title': '', 'content': 'name:Smith, John; city:NY'}])

    def test_quoted_field_with_newline_stays_one_row(self):
        paragraphs = self._parse('name,note\n"a\nb",c\n')[0]['paragraphs']
        self.assertEqual(paragraphs, [{'title': '', 'content': 'name:a\nb; note:c'}])

    def test_escaped_quotes_are_unescaped(self):
        paragraphs = self._parse('name\n"O""Brien"\n')[0]['paragraphs']
        self.assertEqual(paragraphs, [{'title': '', 'content': 'name:O"Brien'}])

    def test_crlf_line_endings_do_not_leak_carriage_returns(self):
        paragraphs = self._parse('name,city\r\nJohn,NY\r\n')[0]['paragraphs']
        self.assertEqual(paragraphs, [{'title': '', 'content': 'name:John; city:NY'}])

    def test_plain_csv_is_unchanged(self):
        paragraphs = self._parse('name,city\nJohn,NY\nJane,LA\n')[0]['paragraphs']
        self.assertEqual(paragraphs, [
            {'title': '', 'content': 'name:John; city:NY'},
            {'title': '', 'content': 'name:Jane; city:LA'},
        ])

    def test_empty_and_header_only_files_yield_no_paragraphs(self):
        for csv_text in ('', 'name,city\n', '\n'):
            with self.subTest(csv_text=csv_text):
                self.assertEqual(self._parse(csv_text), [{'name': 'test.csv', 'paragraphs': []}])

    def test_matches_csv_reader_oracle(self):
        """Differential check against the csv module the sibling handles use."""
        cases = [
            'a,b\n1,2\n',
            'a,b\n"1,5",2\n',
            'a,b\n"x\ny",2\n"z",3\n',
            'a,b,c\n"1""",2,3\n',
            'a,b\r\n1,2\r\n"3,4",5\r\n',
            'name\n"multi\nline\nvalue"\n',
            'a,b\n,2\n1,\n',
            'a,b\n" lead",trail \n',
            'a,b\n\n1,2\n',
            'a,b\n""x"",2\n',
        ]
        for csv_text in cases:
            with self.subTest(csv_text=csv_text):
                rows = [row for row in csv.reader(io.StringIO(csv_text)) if row]
                title = rows[0]
                expected = ['; '.join([f'{key}:{value}' for key, value in zip(title, row)])
                            for row in rows[1:]]
                paragraphs = self._parse(csv_text)[0]['paragraphs']
                self.assertEqual([paragraph['content'] for paragraph in paragraphs], expected)
