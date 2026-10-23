"""Upgrade the actual v2 migration graph and preserve representative user data."""

from copy import deepcopy

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.test import TransactionTestCase

V2_BRANCH_MIGRATIONS = [
    ("knowledge", "0010_publicfileaccess"),
    ("knowledge", "0011_knowledgeworkflow_default_model_setting_and_more"),
    ("application", "0015_application_default_model_setting_and_more"),
]
V2_LATEST = [
    ("knowledge", "0011_knowledgeworkflow_default_model_setting_and_more"),
    ("application", "0015_application_default_model_setting_and_more"),
    ("users", "0001_initial"),
    ("system_manage", "0005_resourcemapping"),
    ("models_provider", "0001_initial"),
    ("tools", "0008_toolworkflow_default_model_setting_and_more"),
    ("portal", None),
]
V3_MIGRATIONS = [
    ("application", "0016_v3_upgrade"),
    ("knowledge", "0012_v3_upgrade"),
    ("users", "0002_v3_upgrade"),
    ("system_manage", "0006_v3_upgrade"),
]


class V2MigrationUpgradeTests(TransactionTestCase):
    def setUp(self):
        executor = MigrationExecutor(connection)
        self.latest = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restore_latest)
        executor.migrate(V2_LATEST)
        self.v2_state = executor.loader.project_state([key for key in V2_LATEST if key[1] is not None])

    def restore_latest(self):
        MigrationExecutor(connection).migrate(self.latest)

    def test_upgrade_preserves_public_access_and_all_default_model_settings(self):
        apps = self.v2_state.apps
        access = apps.get_model("knowledge", "PublicFileAccess").objects.create(
            source_type="KNOWLEDGE", source_id="old-kb"
        )
        apps.get_model("application", "ApplicationFolder").objects.get_or_create(
            id="default", defaults={"name": "v2 folder", "lft": 1, "rght": 2, "tree_id": 1, "level": 0}
        )
        saved = []
        for app_label, model_name in (
            ("application", "Application"),
            ("application", "ApplicationVersion"),
            ("knowledge", "KnowledgeWorkflow"),
            ("knowledge", "KnowledgeWorkflowVersion"),
        ):
            model = apps.get_model(app_label, model_name)
            values = {"default_model_setting": {"model_id": "v2-model", "params": {"temperature": 0.25}}}
            # Knowledge references permit orphaned imported resources in v2.
            for field in model._meta.local_fields:
                if field.is_relation and not field.null:
                    values[field.attname] = (
                        "00000000-0000-0000-0000-000000000001" if field.name != "folder" else "default"
                    )
            if model_name == "ApplicationVersion":
                values["application_id"] = saved[0][2]
            obj = model.objects.create(**values)
            saved.append((app_label, model_name, obj.pk, deepcopy(values["default_model_setting"])))

        chat = apps.get_model("application", "Chat").objects.create(
            application_id=saved[0][2], chat_user_id="v2-chat-user", abstract="历史对话"
        )
        record = apps.get_model("application", "ChatRecord").objects.create(
            chat_id=chat.pk, problem_text="旧问题", answer_text="旧答案", index=1, message_tokens=12, answer_tokens=23
        )
        anonymous_chat = apps.get_model("application", "Chat").objects.create(application_id=saved[0][2])
        apps.get_model("application", "ChatRecord").objects.create(
            chat_id=anonymous_chat.pk, index=1, message_tokens=3, answer_tokens=4
        )
        embedding = apps.get_model("knowledge", "Embedding").objects.create(
            id="v2-vector",
            source_id="v2-paragraph",
            embedding="[0.1,0.2,0.3]",
            document_id="00000000-0000-0000-0000-000000000001",
            knowledge_id="00000000-0000-0000-0000-000000000001",
            paragraph_id="00000000-0000-0000-0000-000000000001",
            meta={"v2": True},
        )
        executor = MigrationExecutor(connection)
        executor.migrate(self.latest)
        current = executor.loader.project_state(self.latest).apps
        self.assertEqual(
            current.get_model("knowledge", "PublicFileAccess").objects.get(pk=access.pk).source_id, "old-kb"
        )
        for app_label, model_name, pk, value in saved:
            self.assertEqual(current.get_model(app_label, model_name).objects.get(pk=pk).default_model_setting, value)
        record = current.get_model("application", "ChatRecord").objects.get(pk=record.pk)
        self.assertEqual((record.problem_text, record.answer_text), ("旧问题", "旧答案"))
        quota = current.get_model("system_manage", "ChatUserTokenQuota").objects.get(user_id="v2-chat-user")
        self.assertEqual((quota.used_tokens, quota.total_tokens), (35, 35))
        self.assertFalse(
            current.get_model("system_manage", "ChatUserTokenQuota").objects.filter(user_id="None").exists()
        )
        embedding = current.get_model("knowledge", "Embedding").objects.get(pk=embedding.pk)
        self.assertEqual(embedding.embedding, "[0.1,0.2,0.3]")
        self.assertEqual(embedding.meta, {"v2": True})
        with connection.cursor() as cursor:
            for table, expected in (
                ("file", "storage_type"),
                ("application_chat", "execute_type"),
                ("application_chat_record", "messages"),
            ):
                columns = connection.introspection.get_table_description(cursor, table)
                self.assertIn(expected, {column.name for column in columns})
        applied = MigrationRecorder(connection).applied_migrations()
        self.assertTrue(set(V2_BRANCH_MIGRATIONS).issubset(applied))
        self.assertTrue(set(V3_MIGRATIONS).issubset(applied))
        executor = MigrationExecutor(connection)
        self.assertEqual(executor.migration_plan(self.latest), [])
        executor.migrate(self.latest)

    def test_older_v2_database_without_default_model_migrations(self):
        targets = [
            ("knowledge", "0010_publicfileaccess"),
            ("application", "0014_applicationversion_knowledge_ids"),
            *V2_LATEST[2:],
        ]
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        apps = executor.loader.project_state([key for key in targets if key[1] is not None]).apps
        row = apps.get_model("knowledge", "PublicFileAccess").objects.create(source_type="FILE", source_id="old-file")
        executor = MigrationExecutor(connection)
        executor.migrate(self.latest)
        current = executor.loader.project_state(self.latest).apps
        self.assertEqual(
            current.get_model("knowledge", "PublicFileAccess").objects.get(pk=row.pk).source_id, "old-file"
        )
        self.assertTrue(set(V2_BRANCH_MIGRATIONS).issubset(MigrationRecorder(connection).applied_migrations()))
        self.assertEqual(MigrationExecutor(connection).migration_plan(self.latest), [])

    def test_v2_base_without_branch_specific_migrations(self):
        executor = MigrationExecutor(connection)
        executor.migrate(
            [
                ("knowledge", "0009_document_user"),
                ("application", "0014_applicationversion_knowledge_ids"),
                *V2_LATEST[2:],
            ]
        )
        self.assertFalse(set(V2_BRANCH_MIGRATIONS) & MigrationRecorder(connection).applied_migrations().keys())
        MigrationExecutor(connection).migrate(self.latest)
        self.assertTrue(set(V2_BRANCH_MIGRATIONS).issubset(MigrationRecorder(connection).applied_migrations()))
        self.assertEqual(MigrationExecutor(connection).migration_plan(self.latest), [])
