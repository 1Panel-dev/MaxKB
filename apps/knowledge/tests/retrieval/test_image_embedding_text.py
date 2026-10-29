"""Image links must not become text vectors competing with actual image content."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import SourceType
from knowledge.vector.base_vector import chunk_data
from knowledge.vector.milvus_vector import MilvusVector
from knowledge.vector.pg_vector import PGVector


class ImageEmbeddingTextTests(SimpleTestCase):
    def row(self, text, **kwargs):
        return {
            "source_type": SourceType.PARAGRAPH,
            "paragraph_id": "paragraph",
            "document_id": "document",
            "knowledge_id": "knowledge",
            "source_id": "paragraph",
            "text": text,
            **kwargs,
        }

    def test_rebuilding_legacy_image_chunks_removes_markup_and_file_ids(self):
        text = "小猫\n![image.png](./oss/file/00000000-0000-0000-0000-000000000001)"
        old_chunks = ["小猫\n![image.png](.", "/oss/file/00000000-0000-0000-0000-000000000001)"]
        # The indexing query also appends asset captions, which may just be filenames.
        embedding_text = f"标题\n{text}\nimage.png\n"
        row = self.row(embedding_text, chunks=old_chunks, paragraph_content=text)

        result = chunk_data(row)

        self.assertEqual([item["text"] for item in result], ["小猫"])
        self.assertEqual(row["text"], embedding_text)
        self.assertEqual(row["chunks"], old_chunks)
        self.assertEqual(result[0]["source_id"], "paragraph")

    def test_recognized_description_ocr_and_surrounding_text_are_preserved(self):
        row = self.row(
            '正文\n![女性肖像 \\[汉服\\]](./oss/file/image-id?download=1 "原图")\n后续文字\nOCR 文字',
            chunks=["obsolete chunks"],
        )

        result = " ".join(" ".join(item["text"] for item in chunk_data(row)).split())

        for expected in ("正文", "女性肖像 [汉服]", "后续文字", "OCR 文字"):
            self.assertIn(expected, result)
        for unwanted in ("./oss/file", "image-id", "download=1", "obsolete chunks", "原图"):
            self.assertNotIn(unwanted, result)

    def test_internal_external_and_data_image_urls_are_removed_before_splitting(self):
        for url in (
            "./oss/file/file-id",
            "/admin/oss/file/file-id",
            "https://example.com/chart(1).png",
            "data:image/png;base64," + "a" * 600,
        ):
            with self.subTest(url=url[:50]):
                result = chunk_data(self.row(f"前文 ![图片描述]({url}) 后文"))
                self.assertEqual(" ".join(" ".join(item["text"] for item in result).split()), "前文 图片描述 后文")

    def test_image_only_markup_does_not_create_empty_or_filename_vectors(self):
        for caption in ("", "image.png", "photo.JPG", "图片.webp"):
            with self.subTest(caption=caption):
                self.assertEqual(chunk_data(self.row(f"![{caption}](./oss/file/file-id)")), [])

    def test_image_descriptions_respect_the_document_child_length(self):
        result = chunk_data(self.row("![" + "描述" * 30 + "](./oss/file/file-id)", child_length=12))

        self.assertEqual("".join(item["text"] for item in result), "描述" * 30)
        self.assertTrue(all(len(item["text"]) <= 12 for item in result))

    def test_text_only_and_non_paragraph_rows_keep_their_existing_chunks(self):
        row = self.row("正文", chunks=["自定义分块一", "自定义分块二"])
        self.assertEqual([item["text"] for item in chunk_data(row)], row["chunks"])
        problem = {**row, "source_type": SourceType.PROBLEM}
        self.assertEqual(chunk_data(problem), [problem])

    def test_both_vector_backends_receive_clean_text_with_original_source_metadata(self):
        for vector in (PGVector(), MilvusVector()):
            with (
                self.subTest(vector=type(vector).__name__),
                patch.object(vector, "save_pre_handler"),
                patch.object(vector, "_batch_save") as save,
            ):
                row = self.row("小猫\n![image.png](./oss/file/file-id)")

                vector.batch_save([row], MagicMock(), lambda: False)

                saved_rows = save.call_args.args[0]
                self.assertEqual([item["text"] for item in saved_rows], ["小猫"])
                for field in ("source_id", "source_type", "paragraph_id", "document_id", "knowledge_id"):
                    self.assertEqual(saved_rows[0][field], row[field])
