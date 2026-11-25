from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.common import WorkflowType
from application.workflow.file_access import (
    WORKFLOW_GENERATED,
    generated_file_target,
    get_authorized_file,
    root_context,
)
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import FileSourceType
from knowledge.services.retrieval_access import inherited_retrieval_context

FILE_ID = "019a0000-0000-7000-8000-000000000001"
USER = "019a0000-0000-7000-8000-0000000000aa"
OTHER_USER = "019a0000-0000-7000-8000-0000000000bb"
APP = "019a0000-0000-7000-8000-0000000000c1"
CHAT = "019a0000-0000-7000-8000-0000000000c2"
OTHER_CHAT = "019a0000-0000-7000-8000-0000000000c3"
TOOL_A = "019a0000-0000-7000-8000-0000000000d1"
TOOL_B = "019a0000-0000-7000-8000-0000000000d2"
KNOWLEDGE = "019a0000-0000-7000-8000-0000000000e1"


def _file(source_type, source_id=None, **meta):
    return SimpleNamespace(id=FILE_ID, source_type=source_type, source_id=source_id, meta=meta)


def _app_root(user=USER):
    return root_context("ANONYMOUS_USER", user, WorkflowType.APPLICATION, APP, CHAT)


def _sub_tool(root, tool_id):
    """模拟应用/工具工作流调用工具工作流:子工作流只带自身 tool_id 与继承的上下文"""
    return {"tool_id": tool_id, **inherited_retrieval_context(root)}


class WorkflowFileAccessTests(SimpleTestCase):
    def _get(self, file, params):
        query_set = MagicMock()
        query_set.filter.return_value.first.return_value = file
        with patch("application.workflow.file_access.QuerySet", return_value=query_set):
            return get_authorized_file(FILE_ID, params)

    def assertDenied(self, file, params):
        with self.assertRaises(AppUnauthorizedFailed):
            self._get(file, params)

    def test_own_chat_upload_is_allowed(self):
        file = _file(FileSourceType.CHAT, CHAT, user_id=USER)
        self.assertIs(self._get(file, _app_root()), file)

    def test_another_users_upload_is_denied(self):
        self.assertDenied(_file(FileSourceType.CHAT, CHAT, user_id=OTHER_USER), _app_root())

    @patch("application.workflow.file_access._is_knowledge_bound", return_value=False)
    def test_unbound_knowledge_source_file_is_denied(self, _bound):
        # GHSA-wmwc-4v38-3ccv:匿名访客提交未关联知识库的源文件 id
        self.assertDenied(_file(FileSourceType.KNOWLEDGE, KNOWLEDGE, user_id=OTHER_USER), _app_root())

    @patch("application.workflow.file_access._is_knowledge_bound", return_value=True)
    def test_knowledge_bound_to_root_application_is_allowed(self, bound):
        file = _file(FileSourceType.KNOWLEDGE, KNOWLEDGE, user_id=OTHER_USER)
        self.assertIs(self._get(file, _app_root()), file)
        self.assertEqual(bound.call_args.args[1:], (APP, KNOWLEDGE))

    def test_application_file_is_bound_to_root_chat(self):
        same_chat = _file(FileSourceType.APPLICATION, APP, chat_id=CHAT)
        self.assertIs(self._get(same_chat, _app_root()), same_chat)
        self.assertDenied(_file(FileSourceType.APPLICATION, APP, chat_id=OTHER_CHAT), _app_root())

    def test_tool_workflow_called_by_application_reads_application_file(self):
        # 应用 -> 工具工作流:按根应用放行渠道上传等应用文件
        file = _file(FileSourceType.APPLICATION, APP, chat_id=CHAT)
        self.assertIs(self._get(file, _sub_tool(_app_root(), TOOL_A)), file)
        self.assertDenied(_file(FileSourceType.APPLICATION, APP, chat_id=OTHER_CHAT), _sub_tool(_app_root(), TOOL_A))

    def test_tool_workflow_called_by_knowledge_workflow_reads_knowledge_file(self):
        root = root_context("SYSTEM_USER", USER, WorkflowType.KNOWLEDGE, KNOWLEDGE)
        file = _file(FileSourceType.KNOWLEDGE, KNOWLEDGE, user_id=OTHER_USER)
        self.assertIs(self._get(file, _sub_tool(root, TOOL_A)), file)

    def test_nested_tool_reads_file_generated_upstream_in_same_run(self):
        # 应用 -> 工具 A -> 工具 B:A 生成的文件存为根对话的 CHAT 文件,B 按发起者读取
        params_a = _sub_tool(_app_root(), TOOL_A)
        source_type, source_id, meta = generated_file_target(params_a)
        file = _file(source_type, source_id, **meta)
        self.assertIs(self._get(file, _sub_tool(params_a, TOOL_B)), file)

    def test_tool_file_generated_by_another_run_is_denied(self):
        root = root_context("SYSTEM_USER", USER, WorkflowType.TOOL, TOOL_A)
        self.assertDenied(_file(FileSourceType.TOOL, TOOL_A, user_id=OTHER_USER, workflow_generated=True), root)

    def test_knowledge_file_generated_by_another_admin_stays_shared(self):
        root = root_context("SYSTEM_USER", USER, WorkflowType.KNOWLEDGE, KNOWLEDGE)
        file = _file(FileSourceType.KNOWLEDGE, KNOWLEDGE, user_id=OTHER_USER)
        self.assertIs(self._get(file, root), file)

    def test_trigger_run_only_reads_its_own_generated_files(self):
        root = root_context("ANONYMOUS_USER", "019a0000-0000-7000-8000-0000000000f1", WorkflowType.TOOL, TOOL_A)
        self.assertDenied(_file(FileSourceType.TEMPORARY_120_MINUTE, user_id=OTHER_USER), root)
        source_type, source_id, meta = generated_file_target(root)
        generated = _file(source_type, source_id, **meta)
        self.assertIs(self._get(generated, root), generated)

    def test_missing_or_malformed_file_id_is_denied(self):
        self.assertDenied(None, _app_root())
        with self.assertRaises(AppUnauthorizedFailed):
            get_authorized_file("not-a-uuid", _app_root())
        with self.assertRaises(AppUnauthorizedFailed):
            get_authorized_file(None, _app_root())

    def test_sub_workflows_inherit_root_context(self):
        inherited = inherited_retrieval_context(_app_root())
        self.assertEqual(
            {k: inherited[k] for k in ("root_user_id", "root_workflow_type", "root_resource_id", "root_chat_id")},
            {
                "root_user_id": USER,
                "root_workflow_type": "APPLICATION",
                "root_resource_id": APP,
                "root_chat_id": CHAT,
            },
        )


class GeneratedFileTargetTests(SimpleTestCase):
    def test_application_root_stores_chat_file_of_root_chat(self):
        # 应用 -> 工具工作流生成的文件不再是公开的 TOOL 文件
        source_type, source_id, meta = generated_file_target(_sub_tool(_app_root(), TOOL_A))
        self.assertEqual((source_type, source_id), (FileSourceType.CHAT, CHAT))
        self.assertEqual((meta["user_id"], meta["chat_id"], meta["application_id"]), (USER, CHAT, APP))

    def test_knowledge_root_stores_knowledge_file(self):
        root = root_context("SYSTEM_USER", USER, WorkflowType.KNOWLEDGE, KNOWLEDGE)
        source_type, source_id, meta = generated_file_target(_sub_tool(root, TOOL_A))
        self.assertEqual((source_type, source_id, meta["user_id"]), (FileSourceType.KNOWLEDGE, KNOWLEDGE, USER))

    def test_tool_debug_stores_temporary_file(self):
        root = {**root_context("SYSTEM_USER", USER, WorkflowType.TOOL, TOOL_A), "debug": True}
        source_type, _, meta = generated_file_target(_sub_tool(root, TOOL_B))
        self.assertEqual(source_type, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertEqual(meta["user_id"], USER)

    def test_tool_trigger_stores_marked_tool_file(self):
        root = root_context("ANONYMOUS_USER", USER, WorkflowType.TOOL, TOOL_A)
        source_type, source_id, meta = generated_file_target(root)
        self.assertEqual((source_type, source_id), (FileSourceType.TOOL, TOOL_A))
        self.assertTrue(meta[WORKFLOW_GENERATED])

    def test_missing_root_context_keeps_previous_storage(self):
        source_type, source_id, meta = generated_file_target({"knowledge_id": KNOWLEDGE})
        self.assertEqual(
            (source_type, source_id, meta["knowledge_id"]), (FileSourceType.KNOWLEDGE, KNOWLEDGE, KNOWLEDGE)
        )
        self.assertFalse(meta["debug"])


class GeneratedToolFileOssTests(SimpleTestCase):
    def test_only_workflow_generated_tool_files_require_auth(self):
        from oss.serializers.file import _is_public_file

        self.assertTrue(_is_public_file(_file(FileSourceType.TOOL, TOOL_A, user_id=USER)))  # 工具图标
        self.assertFalse(_is_public_file(_file(FileSourceType.TOOL, TOOL_A, **{WORKFLOW_GENERATED: True})))
        self.assertTrue(_is_public_file(_file(FileSourceType.TEMPORARY_120_MINUTE, user_id=USER)))
        self.assertFalse(_is_public_file(_file(FileSourceType.CHAT, CHAT, user_id=USER)))
