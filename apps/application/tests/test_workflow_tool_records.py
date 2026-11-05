import json
import threading
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID

from django.test import SimpleTestCase

from application.workflow.common import WorkflowType
from application.workflow.i_node import Signal
from application.workflow.nodes.ai_chat_node.tools.tool.workflow import get_workflow_func
from application.workflow.nodes.reply_node.reply_node import ReplyNode
from application.workflow.nodes.tool_workflow_lib_node.tool_workflow_lib_node import ToolWorkflowLibNode
from application.workflow.status import Status
from application.workflow.workflow_manage import WorkflowManage
from common.encoder.encoder import SystemEncoder
from knowledge.models.knowledge_action import State
from tools.models import ToolRecord


class WorkflowToolRecordTests(SimpleTestCase):
    def setUp(self):
        self.tool_id = UUID("00000000-0000-0000-0000-000000000001")
        self.source_id = UUID("00000000-0000-0000-0000-000000000002")
        self.tool = SimpleNamespace(id=self.tool_id, workspace_id="tool-workspace", is_active=True)
        self.input_fields = [{"field": "city", "label": "City", "type": "string"}]
        self.output_fields = [{"field": "weather", "label": "Weather", "default_value": "sunny"}]
        self.version = SimpleNamespace(
            default_model_setting={},
            work_flow={
                "nodes": [
                    {
                        "id": "tool-base-node",
                        "type": "tool-base-node",
                        "x": 0,
                        "y": 0,
                        "properties": {
                            "stepName": "Base",
                            "user_input_field_list": self.input_fields,
                            "user_output_field_list": self.output_fields,
                        },
                    },
                    {
                        "id": "tool-start-node",
                        "type": "tool-start-node",
                        "x": 0,
                        "y": 0,
                        "properties": {"stepName": "Start"},
                    },
                    {
                        "id": "reply",
                        "type": "reply-node",
                        "x": 0,
                        "y": 0,
                        "properties": {
                            "stepName": "Reply",
                            "node_data": {"reply_type": "referencing", "fields": ["global", "city"], "is_result": True},
                        },
                    },
                ],
                "edges": [
                    {
                        "id": "start-reply",
                        "type": "edge",
                        "sourceNodeId": "tool-start-node",
                        "targetNodeId": "reply",
                        "sourceAnchorId": "tool-start-node_right",
                    }
                ],
            },
        )
        query = self.enterContext(
            patch("application.workflow.nodes.tool_workflow_lib_node.tool_workflow_lib_node.QuerySet")
        ).return_value.filter.return_value
        query.order_by.return_value.__getitem__.return_value.first.return_value = self.version
        query.first.return_value = self.tool
        self.enterContext(
            patch("application.workflow.nodes.tool_workflow_lib_node.tool_workflow_lib_node.valid_function")
        )
        # Run the real engine and nodes synchronously; only database I/O and scheduling are replaced.
        self.enterContext(patch.object(WorkflowManage, "_run_async", lambda manager, node: manager._run(node)))
        self.save = self.enterContext(patch.object(ToolRecord, "save", autospec=True))

    def make_node(self, workflow_type=WorkflowType.APPLICATION):
        source_key = {
            WorkflowType.APPLICATION: "application_id",
            WorkflowType.KNOWLEDGE: "knowledge_id",
            WorkflowType.TOOL: "tool_id",
        }[workflow_type]
        parent = MagicMock(workflow_type=workflow_type, signal=None, assertion_end=MagicMock())
        parent.get_parameters.return_value = {"workspace_id": "caller-workspace", source_key: str(self.source_id)}
        parent.workflow.get_next_edge_nodes.return_value = []
        parent.get_reference_field.return_value = "Hangzhou"
        return ToolWorkflowLibNode(
            SimpleNamespace(id="workflow-tool", properties={"stepName": "Weather"}),
            parent,
            lambda _: {
                "tool_lib_id": str(self.tool_id),
                "input_field_list": [{"field": "city", "source": "reference", "value": ["start", "city"]}],
            },
        )

    def saved_record(self):
        self.save.assert_called_once()
        return self.save.call_args.args[0]

    def test_node_execution_saves_record_with_inputs_outputs_and_local_reply_positions(self):
        node = self.make_node()
        node.run()

        record = self.saved_record()
        self.assertEqual(record.tool_id, self.tool_id)
        self.assertEqual(record.workspace_id, self.tool.workspace_id)
        self.assertEqual(record.state, State.SUCCESS)
        self.assertGreaterEqual(record.run_time, 0)
        self.assertEqual(record.meta["input_field_list"], self.input_fields)
        self.assertEqual(record.meta["output_field_list"], self.output_fields)
        self.assertEqual(record.meta["input"], {"city": "Hangzhou"})
        self.assertEqual(record.meta["output"], {"weather": "sunny"})
        self.assertEqual([detail["node_id"] for detail in record.meta["details"]], ["tool-start-node", "reply"])
        self.assertEqual(record.meta["answer_text_list"][0]["content"], "Hangzhou")
        self.assertEqual(record.meta["answer_text_list"][0]["position"]["id"], "reply")
        json.dumps(record.meta, cls=SystemEncoder)
        node.workflow_manage.write_context.assert_called_with("workflow-tool", "weather", "sunny", False)
        forwarded = node.workflow_manage.write.call_args.args[0]
        self.assertEqual(forwarded.position.id, "workflow-tool")
        self.assertEqual(forwarded.position.children.id, "reply")
        self.assertEqual(node.status, Status.SUCCESS)

    def test_record_identifies_application_knowledge_and_parent_tool(self):
        for workflow_type in WorkflowType:
            with self.subTest(workflow_type=workflow_type):
                self.save.reset_mock()
                node = self.make_node(workflow_type)
                node.run()
                record = self.saved_record()
                self.assertEqual(record.source_type, workflow_type.value)
                self.assertEqual(str(record.source_id), str(self.source_id))

    def test_failed_child_execution_is_saved_and_propagated(self):
        node = self.make_node()
        with patch.object(ReplyNode, "execute", side_effect=ValueError("weather unavailable")):
            node.run()

        record = self.saved_record()
        self.assertEqual(record.state, State.FAILURE)
        self.assertEqual(record.meta["details"][-1]["error"], "weather unavailable")
        self.assertEqual(node.status, Status.FAIL)

    def test_failed_detail_is_recorded_even_without_callback_error(self):
        node = self.make_node()
        with (
            patch.object(ReplyNode, "execute", side_effect=ValueError("weather unavailable")),
            patch.object(
                WorkflowManage, "end", lambda manager, error=None: manager.call_back.on_complete(manager, None)
            ),
        ):
            node.run()

        self.assertEqual(self.saved_record().state, State.FAILURE)

    def test_cancellation_is_not_recorded_as_success(self):
        node = self.make_node()
        with patch.object(ReplyNode, "execute", lambda reply: reply.workflow_manage.cancel()):
            node.run()

        self.assertEqual(self.saved_record().state, State.REVOKED)
        self.assertEqual(node.status, Status.CANCELLED)

    def test_record_write_error_finishes_parent_node(self):
        self.save.side_effect = RuntimeError("record storage unavailable")
        node = self.make_node()
        node.run()

        self.assertTrue(node._completed)
        self.assertEqual(node.status, Status.FAIL)
        self.assertEqual(node.data["error"], "record storage unavailable")

    def test_ai_tool_call_still_saves_execution_record(self):
        cancel_event = threading.Event()
        self.addCleanup(cancel_event.set)
        tool = get_workflow_func(
            "APPLICATION", str(self.source_id), self.tool, self.version, "tool-workspace", cancel_event
        )

        self.assertEqual(tool(city="Hangzhou"), {"weather": "sunny"})
        record = self.saved_record()
        self.assertEqual(record.state, State.SUCCESS)
        self.assertEqual(record.source_type, "APPLICATION")
        self.assertEqual(record.meta["input"], {"city": "Hangzhou"})

    def test_form_signal_still_pauses_parent_workflow(self):
        node = self.make_node()
        with patch.object(ReplyNode, "execute", lambda reply: setattr(reply.workflow_manage, "signal", Signal.FORM)):
            node.run()

        self.saved_record()
        self.assertEqual(node.status, Status.SUCCESS)
        self.assertEqual(node.workflow_manage.signal, Signal.FORM)
