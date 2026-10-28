import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import polib
from django.test import SimpleTestCase, override_settings
from django.utils.translation import override
from rest_framework.exceptions import ValidationError

from common.exception.app_exception import AppApiException
from knowledge.models import SearchMode
from knowledge.serializers.external_retrieval import RetrievalRequest
from knowledge.serializers.knowledge import HitTestSerializer
from knowledge.serializers.knowledge_sync import KnowledgeSyncSettingRequest
from knowledge.services.knowledge_archive import validate_archive
from knowledge.services.knowledge_sync_schedule import normalize_knowledge_sync_setting
from knowledge.services.multimodal_retrieval import MAX_QUERY_IMAGE_COUNT, load_image_query_inputs
from knowledge.services.workflow_sync_source import validate_workflow_sync_source
from knowledge.vector.milvus_vector import MilvusVector
from knowledge.vector.pg_vector import PGVector


class KnowledgeTranslationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.knowledge_dir = Path(__file__).resolve().parents[1]
        locale_dir = Path(cls.enterClassContext(TemporaryDirectory()))
        cls.catalogs = {}
        for locale in ("zh_CN", "zh_Hant", "en_US"):
            catalog = polib.pofile(cls.knowledge_dir.parent / "locales" / locale / "LC_MESSAGES" / "django.po")
            cls.catalogs[locale] = catalog
            target = locale_dir / locale / "LC_MESSAGES" / "django.mo"
            target.parent.mkdir(parents=True)
            catalog.save_as_mofile(target)
        # Compile source catalogs in isolation so stale or absent local .mo files cannot hide regressions.
        cls.enterClassContext(override_settings(LOCALE_PATHS=[str(locale_dir)]))

    def test_knowledge_translation_calls_have_catalog_entries(self):
        messages = set()
        for path in self.knowledge_dir.rglob("*.py"):
            if {"tests", "migrations"}.intersection(path.relative_to(self.knowledge_dir).parts):
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id in {"_", "gettext", "gettext_lazy"}
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    messages.add(node.args[0].value)
        self.assertTrue(messages)
        for locale, catalog in self.catalogs.items():
            for message in sorted(messages):
                with self.subTest(locale=locale, message=message):
                    entry = catalog.find(message)
                    self.assertIsNotNone(entry)
                    self.assertNotIn("fuzzy", entry.flags)
                    if locale != "en_US" or not message.isascii():
                        self.assertTrue(entry.translated())

    def test_image_embedding_error_follows_active_language_for_both_vector_backends(self):
        model = MagicMock()
        model.supports_image_embedding.return_value = False
        for language, expected in (
            ("zh-cn", "当前向量模型不支持图片向量化"),
            ("zh-hant", "目前向量模型不支援圖片向量化"),
            ("en-us", "The current embedding model does not support image embedding"),
        ):
            for backend in (PGVector, MilvusVector):
                with self.subTest(language=language, backend=backend.__name__), override(language):
                    with self.assertRaises(AppApiException) as raised:
                        backend().hit_test("", ["knowledge-id"], [], 5, 0.6, SearchMode.embedding, model, ["image"])
                    self.assertEqual(raised.exception.code, 500)
                    self.assertEqual(str(raised.exception.message), expected)
        model.embed_images.assert_not_called()
        model.embed_query.assert_not_called()

    @override("zh-cn")
    def test_query_validation_is_translated(self):
        serializer = HitTestSerializer(data={"top_number": 5, "similarity": 0.6, "search_mode": "embedding"})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["non_field_errors"][0]), "查询文本和查询图片不能同时为空")

        serializer = RetrievalRequest(data={"query_text": 123})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["query_text"][0]), "查询文本必须是字符串。")

    @override("zh-cn")
    def test_translated_errors_preserve_format_arguments(self):
        with self.assertRaises(AppApiException) as raised:
            load_image_query_inputs([{}] * (MAX_QUERY_IMAGE_COUNT + 1))
        self.assertEqual(str(raised.exception.message), f"每次最多可查询 {MAX_QUERY_IMAGE_COUNT} 张图片")

        with self.assertRaisesMessage(ValueError, "日期必须介于 1 和 7 之间"):
            normalize_knowledge_sync_setting(
                {"schedule_type": "weekly", "sync_type": "incremental", "time": ["01:00"], "days": [8]}
            )

    @override("zh-cn")
    def test_schedule_validation_is_translated(self):
        for setting, expected in (
            ({"schedule_type": "cron", "cron_expression": "invalid"}, "Cron 表达式无效"),
            (
                {"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 1},
                "同步间隔不能少于 5 分钟",
            ),
        ):
            with self.subTest(setting=setting):
                serializer = KnowledgeSyncSettingRequest(data={"enabled": True, "sync_type": "incremental", **setting})
                self.assertFalse(serializer.is_valid())
                self.assertEqual(str(serializer.errors["non_field_errors"][0]), expected)

        with self.assertRaisesMessage(ValueError, "启用定时同步前，请先运行一次工作流"):
            validate_workflow_sync_source({}, {})

    def test_archive_validation_follows_active_language(self):
        for language, expected in (
            ("zh-cn", "不支持该知识库归档版本。"),
            ("zh-hant", "不支援此知識庫封存檔版本。"),
            ("en-us", "Unsupported knowledge archive version."),
        ):
            with self.subTest(language=language), override(language):
                with self.assertRaises(ValidationError) as raised:
                    validate_archive({"archive_version": -1}, None)
                self.assertEqual(str(raised.exception.detail[0]), expected)
