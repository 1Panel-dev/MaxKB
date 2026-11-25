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
