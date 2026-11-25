from unittest.mock import patch
from django.test import SimpleTestCase, TestCase
from application.serializers.application import validate_application_bindings
from common.exception.app_exception import AppApiException


class ApplicationBindingTests(SimpleTestCase):
    @patch("application.serializers.application.get_authorized_application_ids", return_value=[])
    def test_nested_application_node_checks_single_reference(self, authorized):
        node = {"type": "application-node", "properties": {"node_data": {"application_id": "child"}}}
        loop = {"type": "loop-node", "properties": {"node_data": {"loop_body": {"nodes": [node]}}}}
        with self.assertRaises(AppApiException):
            validate_application_bindings("author", "workspace", {"work_flow": {"nodes": [loop]}})
        authorized.assert_called_once_with("author", "workspace", ["child"])


class ToolBindingTests(SimpleTestCase):
    @patch("common.utils.workflow_reference.get_authorized_tool_ids", return_value=["shared"])
    def test_batch_requires_every_reference(self, authorized):
        from common.utils.workflow_reference import require_workflow_tools

        with self.assertRaises(AppApiException):
            require_workflow_tools(["shared", "restricted"], "actor", "workspace")
        authorized.assert_called_once_with("actor", "workspace", ["shared", "restricted"])


class McpBindingTests(SimpleTestCase):
    @patch(
        "application.workflow.nodes.ai_chat_node.tools.mcp.require_workflow_tools",
        side_effect=AppApiException(403, "denied"),
    )
    def test_resolving_mcp_config_requires_the_workflow_actor(self, authorize):
        from application.workflow.nodes.ai_chat_node.tools.mcp import get_referenced_mcp_tools

        with self.assertRaises(AppApiException):
            get_referenced_mcp_tools(["tool"], {"workflow_user_id": "actor", "workspace_id": "team"})
        authorize.assert_called_once_with(["tool"], "actor", "team")


class DatasourceAuthorizationTests(SimpleTestCase):
    @patch("knowledge.serializers.knowledge_workflow.get_node_class")
    @patch("knowledge.serializers.knowledge_workflow.Knowledge.objects.filter")
    def test_only_the_builtin_form_method_is_dispatched(self, knowledge, get_node):
        from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowSerializer

        knowledge.return_value.values_list.return_value.first.return_value = "team"
        identifier = "00000000-0000-0000-0000-000000000001"
        data = {
            "knowledge_id": identifier,
            "user_id": identifier,
            "type": "local",
            "id": "data-source-local-node",
            "params": {},
        }
        with self.assertRaises(AppApiException):
            KnowledgeWorkflowSerializer.Datasource(data={**data, "function_name": "other"}).action()
        get_node.assert_not_called()
        KnowledgeWorkflowSerializer.Datasource(data={**data, "function_name": "get_form_list"}).action()
        get_node.return_value.get_form_list.assert_called_once_with()


class WorkflowExportScopeTests(TestCase):
    def test_export_checks_each_workspace_before_loading_nested_contents(self):
        from common.auth.struct.auth import Auth
        from common.utils.workflow_reference import get_exportable_tools
        from tools.models import Tool, ToolFolder, ToolScope, ToolType, ToolWorkflow
        from users.models import User

        user = User.objects.create(username="export-test", role="ADMIN")
        folder, _ = ToolFolder.objects.get_or_create(id="default", defaults={"name": "default"})
        local = Tool.objects.create(name="local", folder=folder, workspace_id="alpha", tool_type=ToolType.WORKFLOW)
        shared = Tool.objects.create(name="shared", folder=folder, workspace_id="None", scope=ToolScope.SHARED)
        foreign = Tool.objects.create(name="foreign", folder=folder, workspace_id="bravo")
        with patch("common.utils.workflow_reference.get_auth", return_value=Auth({"ADMIN"}, {})):
            result = get_exportable_tools({"tool_ids": [str(local.id), str(shared.id)]}, "alpha", user.id)
            self.assertEqual([item.id for item in result], [local.id])
            ToolWorkflow.objects.create(
                tool=local,
                workspace_id="alpha",
                work_flow={
                    "nodes": [{"type": "tool-lib-node", "properties": {"node_data": {"tool_lib_id": str(foreign.id)}}}]
                },
            )
            with self.assertRaises(AppApiException):
                get_exportable_tools({"tool_ids": [str(local.id)]}, "alpha", user.id)
