# coding=utf-8
import asyncio
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class McpNodeToolErrorTestCase(unittest.TestCase):
    def load_node_module(self, call_tool):
        # Isolate Django and the MCP sandbox so the node can be tested without a database.
        backend = SimpleNamespace(call_tool=call_tool)
        dependencies = {
            'application.flow.backend.sandbox_mcp': SimpleNamespace(SandboxMCPBackend=Mock(return_value=backend)),
            'application.flow.i_step_node': SimpleNamespace(
                NodeResult=lambda node_variable, workflow_variable: SimpleNamespace(
                    node_variable=node_variable, workflow_variable=workflow_variable
                )
            ),
            'application.flow.step_node.mcp_node.i_mcp_node': SimpleNamespace(IMcpNode=object),
            'common.utils.shared_resource_auth': SimpleNamespace(
                get_runtime_user_id=Mock(), validate_authorized_tool_ids=Mock()
            ),
            'common.utils.tool_code': SimpleNamespace(
                ToolExecutor=Mock(return_value=SimpleNamespace(validate_mcp_transport=Mock()))
            ),
            'django.db.models': SimpleNamespace(QuerySet=Mock()),
            'tools.models': SimpleNamespace(Tool=Mock()),
        }
        source = Path(__file__).parent / 'flow/step_node/mcp_node/impl/base_mcp_node.py'
        spec = importlib.util.spec_from_file_location('base_mcp_node_under_test', source)
        module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', dependencies):
            spec.loader.exec_module(module)
        return module

    @staticmethod
    def text_content(*texts):
        return [SimpleNamespace(text=text) for text in texts]

    def execute(self, result):
        async def call_tool(mcp_server, mcp_tool, params):
            return result

        module = self.load_node_module(call_tool)
        return module.BaseMcpNode().execute('{}', 'demo', 'close_ticket', None, 'select', {})

    def test_raising_node_error_when_the_tool_reports_is_error(self):
        result = SimpleNamespace(
            isError=True, content=self.text_content('Ticket T-1001 cannot be closed: it has open sub-tasks')
        )
        with self.assertRaises(Exception) as raised:
            self.execute(result)
        self.assertEqual(
            str(raised.exception),
            'MCP tool close_ticket execution failed: Ticket T-1001 cannot be closed: it has open sub-tasks',
        )

    def test_keeping_the_error_text_without_a_content_message(self):
        result = SimpleNamespace(isError=True, content=[])
        with self.assertRaises(Exception) as raised:
            self.execute(result)
        self.assertEqual(str(raised.exception), 'MCP tool close_ticket execution failed')

    def test_returning_the_tool_result_when_is_error_is_not_set(self):
        result = SimpleNamespace(isError=False, content=self.text_content('T-1001 is open'))
        node_result = self.execute(result)
        self.assertEqual(node_result.node_variable['result'], ['T-1001 is open'])
        self.assertEqual(node_result.node_variable['mcp_tool'], 'close_ticket')
        self.assertEqual(node_result.workflow_variable, {})


if __name__ == '__main__':
    unittest.main()
