from unittest.mock import patch
from django.test import SimpleTestCase
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
