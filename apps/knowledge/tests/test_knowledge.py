from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from knowledge.models import (
    KnowledgeType,
)
from knowledge.serializers.knowledge import (
    KnowledgeSerializer,
)
from knowledge.services.document_strategy import (
    normalize_document_strategy,
)
from knowledge.services.knowledge_sync_schedule import (
    DEFAULT_KNOWLEDGE_SYNC_SETTING,
)
from knowledge.task.sync import (
    scheduled_sync_web_knowledge,
)


class WebKnowledgeCreationTests(SimpleTestCase):
    def setUp(self):
        self.save = self.enterContext(patch("knowledge.serializers.knowledge.Knowledge.save", autospec=True))
        self.enterContext(patch("knowledge.serializers.knowledge.UserResourcePermissionSerializer"))
        self.enterContext(patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge"))
        self.crawl = self.enterContext(patch("knowledge.serializers.knowledge.sync_web_knowledge.delay"))
        self.deploy_schedule = self.enterContext(
            patch("knowledge.serializers.knowledge.deploy_knowledge_sync_job.delay")
        )

    def create_web(self, with_valid=True):
        serializer = KnowledgeSerializer.Create(
            data={"user_id": "00000000-0000-0000-0000-000000000012", "workspace_id": "default"}
        )
        response = serializer.save_web(
            {
                "name": "Web docs",
                "folder_id": "default",
                "embedding_model_id": "00000000-0000-0000-0000-000000000013",
                "source_url": "https://example.com",
                "selector": ".content",
                "doc_strategy": {"split": {"max_length": 1024}},
            },
            with_valid=with_valid,
        )
        return self.save.call_args.args[0], response

    def test_web_creation_persists_and_returns_disabled_default_sync_setting(self):
        for with_valid in (True, False):
            with self.subTest(with_valid=with_valid):
                self.save.reset_mock()
                self.crawl.reset_mock()
                knowledge, response = self.create_web(with_valid)
                self.save.assert_called_once()
                self.assertEqual(knowledge.meta["sync_setting"], DEFAULT_KNOWLEDGE_SYNC_SETTING)
                self.assertFalse(knowledge.meta["sync_setting"]["enabled"])
                self.assertEqual(response["meta"]["sync_setting"], DEFAULT_KNOWLEDGE_SYNC_SETTING)
                self.assertEqual(knowledge.meta["doc_strategy"]["split"]["max_length"], 1024)
                self.crawl.assert_called_once_with(
                    str(knowledge.id),
                    "00000000-0000-0000-0000-000000000012",
                    "https://example.com",
                    ".content",
                    knowledge.meta["doc_strategy"],
                )
                self.deploy_schedule.assert_not_called()

    def test_sync_defaults_are_independent_between_created_knowledge_bases(self):
        first, _response = self.create_web()
        first.meta["sync_setting"]["enabled"] = True
        first.meta["sync_setting"]["time"].append("02:00")
        second, _response = self.create_web()
        self.assertFalse(second.meta["sync_setting"]["enabled"])
        self.assertEqual(second.meta["sync_setting"]["time"], ["01:00"])
        self.assertFalse(DEFAULT_KNOWLEDGE_SYNC_SETTING["enabled"])
        self.assertEqual(DEFAULT_KNOWLEDGE_SYNC_SETTING["time"], ["01:00"])


class KnowledgeModelUpdateTests(SimpleTestCase):
    @patch("knowledge.task.sync.QuerySet")
    @patch("knowledge.serializers.knowledge.sync_replace_web_knowledge.delay")
    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_saved_strategy_takes_effect_on_next_manual_or_scheduled_sync(
        self, query_set, _update_mapping, delay, task_query_set
    ):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000011",
            user_id="00000000-0000-0000-0000-000000000013",
            type=KnowledgeType.WEB,
            meta={
                "source_url": "https://example.com",
                "selector": "body",
                "doc_strategy": normalize_document_strategy(None),
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
            },
        )
        query_set.return_value.get.return_value = knowledge
        task_query_set.return_value.filter.return_value.first.return_value = knowledge
        operation = KnowledgeSerializer.Operate(
            data={"workspace_id": "default", "knowledge_id": knowledge.id, "user_id": knowledge.user_id}
        )
        strategy = normalize_document_strategy(
            {
                "split": {"max_length": 1024},
                "visual": {"enabled": True, "model_id": "00000000-0000-0000-0000-000000000042"},
                "index": {"title_as_question": True},
            }
        )

        KnowledgeSerializer.Operate.edit.__wrapped__(operation, {"doc_strategy": strategy}, select_one=False)

        delay.assert_not_called()
        self.assertEqual(knowledge.meta["doc_strategy"], strategy)
        self.assertEqual(knowledge.meta["source_url"], "https://example.com")
        sync = KnowledgeSerializer.SyncWeb(data={"user_id": knowledge.user_id})
        for sync_type in ("incremental", "replace", "complete"):
            with self.subTest(sync_type=sync_type):
                delay.reset_mock()
                getattr(sync, f"{sync_type}_sync")(knowledge)
                delay.assert_called_once()
                self.assertEqual(delay.call_args.args[4], strategy)
                self.assertEqual(delay.call_args.args[5], sync_type)

                delay.reset_mock()
                knowledge.meta["sync_setting"]["sync_type"] = sync_type
                self.assertTrue(scheduled_sync_web_knowledge.run(str(knowledge.id)))
                delay.assert_called_once()
                self.assertEqual(delay.call_args.args[4], strategy)
                self.assertEqual(delay.call_args.args[5], sync_type)

    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_model_update_preserves_meta_when_strategy_is_omitted_or_inapplicable_null(self, query_set, update_mapping):
        knowledge_id = "00000000-0000-0000-0000-000000000011"
        model_id = "00000000-0000-0000-0000-000000000012"
        for knowledge_type in KnowledgeType:
            payloads = [{"embedding_model_id": model_id}]
            if knowledge_type != KnowledgeType.WEB:
                payloads.append({"embedding_model_id": model_id, "doc_strategy": None})
            for payload in payloads:
                with self.subTest(knowledge_type=knowledge_type, payload=payload):
                    original_meta = {"sync_setting": {"enabled": True}}
                    if knowledge_type == KnowledgeType.WEB:
                        original_meta["doc_strategy"] = normalize_document_strategy({"split": {"max_length": 1024}})
                    knowledge = MagicMock(id=knowledge_id, type=knowledge_type, meta=original_meta.copy())
                    query_set.return_value.get.return_value = knowledge
                    operation = KnowledgeSerializer.Operate(
                        data={
                            "user_id": "00000000-0000-0000-0000-000000000013",
                            "workspace_id": "workspace-id",
                            "knowledge_id": knowledge_id,
                        }
                    )

                    # Exercise the edit path with mocked persistence, without opening a database transaction.
                    KnowledgeSerializer.Operate.edit.__wrapped__(operation, payload, select_one=False)

                    self.assertEqual(knowledge.embedding_model_id, model_id)
                    self.assertEqual(knowledge.meta, original_meta)
                    knowledge.save.assert_called_once_with()
                    update_mapping.assert_called_with(knowledge_id)

    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_web_knowledge_explicit_null_strategy_still_resets_to_defaults(self, query_set, _update_mapping):
        knowledge = MagicMock(
            type=KnowledgeType.WEB,
            meta={"selector": "body", "doc_strategy": {"split": {"max_length": 1024}}},
        )
        query_set.return_value.get.return_value = knowledge
        operation = KnowledgeSerializer.Operate(
            data={
                "user_id": "00000000-0000-0000-0000-000000000013",
                "workspace_id": "workspace-id",
                "knowledge_id": "00000000-0000-0000-0000-000000000011",
            }
        )

        KnowledgeSerializer.Operate.edit.__wrapped__(operation, {"doc_strategy": None}, select_one=False)

        self.assertEqual(knowledge.meta, {"selector": "body", "doc_strategy": normalize_document_strategy(None)})
        knowledge.save.assert_called_once_with()
