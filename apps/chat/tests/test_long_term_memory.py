import json
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase
from langchain_core.messages import AIMessageChunk

from application import long_term_memory
from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationLongTermMemory,
    ApplicationVersion,
    ChatRecord,
)
from application.workflow.workflow_manage import WorkflowManage
from chat.serializers.chat import ChatSerializers


class LongTermMemoryTests(TestCase):
    questions = [f"For future answers, remember preference {i}." for i in range(1, 8)]

    def setUp(self):
        self.settings = {
            "long_term_enable": True,
            "long_term_trigger_type": "ROUND",
            "long_term_trigger_setting": {"rounds": 5},
            "long_term_model_id": str(uuid4()),
        }
        workflow = {
            "nodes": [
                self.node("base-node", self.settings),
                self.node("start-node", {}),
                self.node(
                    "reply-node", {"reply_type": "referencing", "fields": ["start-node", "memory"], "is_result": True}
                ),
            ],
            "edges": [
                {
                    "id": "edge",
                    "type": "edge",
                    "sourceNodeId": "start-node",
                    "targetNodeId": "reply-node",
                    "sourceAnchorId": "start-node_right",
                    "targetAnchorId": "reply-node_left",
                }
            ],
        }
        folder = ApplicationFolder.objects.create(id="memory-tests", name="Memory tests")
        self.app = Application.objects.create(name="Memory", folder=folder, type="WORK_FLOW", work_flow=workflow)
        ApplicationVersion.objects.create(application=self.app, type=self.app.type, work_flow=workflow)
        ApplicationAccessToken.objects.create(application=self.app, access_token=str(uuid4()), access_num=100)
        self.chat_id = str(uuid4())
        self.user_id = str(uuid4())
        self.model = self.enterContext(patch.object(long_term_memory, "get_model_instance_by_model_workspace_id"))
        self.model.return_value.stream.return_value = [AIMessageChunk(content="Saved preferences")]
        self.enterContext(patch.object(WorkflowManage, "_run_async", WorkflowManage._run))
        self.enterContext(patch("chat.serializers.chat.get_message_queue"))
        self.enterContext(patch("chat.serializers.chat.resolve_chat_user", return_value={"username": "tester"}))
        self.enterContext(patch("chat.serializers.chat.resolve_chat_user_group", return_value=[]))
        self.dispatch = self.enterContext(patch.object(long_term_memory.extract_long_term_memory, "apply_async"))
        self.dispatch.side_effect = lambda args, kwargs: long_term_memory.extract_long_term_memory(*args, **kwargs)

    @staticmethod
    def node(node_type, data):
        return {
            "id": node_type,
            "type": node_type,
            "x": 0,
            "y": 0,
            "properties": {"stepName": node_type, "node_data": data},
        }

    def ask(self, question, **options):
        serializer = ChatSerializers(
            data={
                "application_id": str(self.app.id),
                "chat_id": self.chat_id,
                "chat_user_id": self.user_id,
                "chat_user_type": "CHAT_USER",
                "ip_address": "127.0.0.1",
                "source": {"type": "ONLINE"},
            }
        )
        with self.captureOnCommitCallbacks(execute=True):
            response = serializer.chat({"stream": False, "message": {"content": question}, **options})
        return json.loads(response.content)["data"]["content"]

    def test_fifth_round_generates_memory_for_subsequent_replies(self):
        for question in self.questions[:5]:
            self.assertEqual(self.ask(question), "")
        self.model.assert_called_once()
        prompt = self.model.return_value.stream.call_args.args[0][0].content
        for question in self.questions[:5]:
            self.assertIn(question, prompt)
        for question in self.questions[5:7]:
            self.assertEqual(self.ask(question), "Saved preferences")
        self.assertEqual(
            ApplicationLongTermMemory.objects.get(application=self.app, chat_user_id=self.user_id).memory,
            "Saved preferences",
        )

    def test_scheduled_memory_reads_structured_and_legacy_messages(self):
        self.settings.update(
            long_term_trigger_type="SCHEDULED",
            long_term_trigger_setting={"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 2},
            long_term_model_id_type="default",
        )
        default_model_id = str(uuid4())
        self.app.default_model_setting = {
            "LLM": {"model_id": default_model_id, "model_params_setting": {"temperature": 0}}
        }
        self.app.save(update_fields=["work_flow", "default_model_setting"])
        ApplicationVersion.objects.filter(application=self.app).update(work_flow=self.app.work_flow)
        self.ask("Use concise answers.")
        self.dispatch.assert_not_called()
        record = ChatRecord.objects.get(chat_id=self.chat_id)
        record.messages = [
            {"type": "REASONING", "content": "internal reasoning"},
            {"type": "TEXT", "content": "Understood."},
        ]
        record.save(update_fields=["messages"])
        ChatRecord.objects.create(
            chat_id=self.chat_id, problem_text="Legacy question", answer_text="Legacy answer", index=0
        )
        long_term_memory._execute_scheduled_extract("default", self.app.id)
        self.model.assert_called_once_with(default_model_id, self.app.workspace_id, temperature=0)
        prompt = self.model.return_value.stream.call_args.args[0][0].content
        self.assertIn("用户：Use concise answers.\nAI：Understood.", prompt)
        self.assertIn("用户：Legacy question\nAI：Legacy answer", prompt)
        self.assertNotIn("internal reasoning", prompt)

    def test_delayed_fifth_round_uses_its_own_history(self):
        self.dispatch.side_effect = None
        for question in self.questions[:6]:
            self.ask(question)
        fifth, sixth = self.dispatch.call_args_list[-2:]
        for call in (fifth, sixth):
            args, kwargs = call.args
            long_term_memory.extract_long_term_memory(*args, **kwargs)
        self.model.assert_called_once()
        prompt = self.model.return_value.stream.call_args.args[0][0].content
        self.assertIn(self.questions[0], prompt)
        self.assertIn(self.questions[4], prompt)
        self.assertNotIn(self.questions[5], prompt)
        self.assertEqual(self.ask(self.questions[6]), "Saved preferences")
