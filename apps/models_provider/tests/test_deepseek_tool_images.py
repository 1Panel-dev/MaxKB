import json
import os
from copy import deepcopy
from unittest import skipUnless

from django.test import SimpleTestCase
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from models_provider.impl.deepseek_model_provider.model.llm import DeepSeekChatModel
from models_provider.tests.image_helpers import image_data_url


def tool_call_message(*ids, reasoning="tool reasoning"):
    return AIMessage(
        content="",
        tool_calls=[{"name": "screenshot", "args": {}, "id": call_id} for call_id in ids],
        additional_kwargs={"reasoning_content": reasoning},
    )


def image_result(call_id, image):
    return ToolMessage(
        content=[{"type": "text", "text": call_id}, {"type": "image_url", "image_url": {"url": image}}],
        tool_call_id=call_id,
    )


class DeepSeekToolImagePayloadTests(SimpleTestCase):
    def setUp(self):
        self.model = DeepSeekChatModel(
            model="test-vision-gateway", api_key="test-key", base_url="http://127.0.0.1:0/v1", max_retries=0
        )

    def _payload(self, messages):
        before = deepcopy([message.model_dump() for message in messages])
        payload = self.model._get_request_payload(messages)
        self.assertEqual([message.model_dump() for message in messages], before)
        return payload["messages"]

    def test_mcp_and_openai_tool_images_are_sent_as_vision_blocks_in_order(self):
        image = image_data_url((2, 3))
        messages = [
            HumanMessage(content="inspect"),
            tool_call_message("call_tool"),
            ToolMessage(
                tool_call_id="call_tool",
                content=[
                    {"type": "text", "text": "screenshot"},
                    {"type": "image", "base64": image.split(",", 1)[1], "mime_type": "image/png"},
                    {"type": "image_url", "image_url": {"url": "https://example.com/second.png", "detail": "low"}},
                ],
                artifact={"keep": "original"},
            ),
        ]
        payload = self._payload(messages)
        self.assertEqual([message["role"] for message in payload], ["user", "assistant", "tool", "user"])
        self.assertEqual(payload[1]["reasoning_content"], "tool reasoning")
        self.assertEqual(payload[2]["tool_call_id"], "call_tool")
        self.assertIsInstance(payload[2]["content"], str)
        self.assertNotIn("image_url", payload[2]["content"])
        self.assertIn("screenshot", payload[2]["content"])
        vision = payload[3]["content"]
        self.assertIn("call_tool", vision[0]["text"])
        self.assertEqual(vision[1]["image_url"]["url"], image)
        self.assertEqual(vision[2]["image_url"], {"url": "https://example.com/second.png", "detail": "low"})

    def test_parallel_tool_responses_precede_the_extra_user_message(self):
        image_a, image_b = image_data_url((2, 3)), image_data_url((4, 5))
        payload = self._payload(
            [
                tool_call_message("call_a", "call_text", "call_b"),
                image_result("call_a", image_a),
                ToolMessage(content="text result", tool_call_id="call_text"),
                image_result("call_b", image_b),
            ]
        )
        self.assertEqual([message["role"] for message in payload], ["assistant", "tool", "tool", "tool", "user"])
        self.assertEqual([message["tool_call_id"] for message in payload[1:4]], ["call_a", "call_text", "call_b"])
        self.assertEqual(payload[2]["content"], "text result")
        vision = payload[-1]["content"]
        self.assertIn("call_a", vision[0]["text"])
        self.assertIn("call_b", vision[2]["text"])
        self.assertEqual(
            [block["image_url"]["url"] for block in vision if block["type"] == "image_url"], [image_a, image_b]
        )

    def test_each_tool_round_keeps_its_reasoning_and_own_images(self):
        image_a, image_b = image_data_url((2, 3)), image_data_url((4, 5))
        payload = self._payload(
            [
                tool_call_message("call_a", reasoning="first reasoning"),
                image_result("call_a", image_a),
                tool_call_message("call_b", reasoning="second reasoning"),
                image_result("call_b", image_b),
                AIMessage(content=[{"type": "text", "text": "answer"}]),
            ]
        )
        self.assertEqual(
            [message["role"] for message in payload],
            ["assistant", "tool", "user", "assistant", "tool", "user", "assistant"],
        )
        self.assertEqual(payload[0]["reasoning_content"], "first reasoning")
        self.assertEqual(payload[3]["reasoning_content"], "second reasoning")
        self.assertEqual(payload[2]["content"][1]["image_url"]["url"], image_a)
        self.assertEqual(payload[5]["content"][1]["image_url"]["url"], image_b)
        self.assertEqual(payload[6]["content"], "answer")

    def test_text_only_tools_and_existing_user_images_are_unchanged(self):
        image = {"type": "image_url", "image_url": {"url": "https://example.com/user.png"}}
        content = [{"type": "text", "text": "text result"}]
        payload = self._payload(
            [
                HumanMessage(content=[image]),
                tool_call_message("call_text"),
                ToolMessage(content=content, tool_call_id="call_text"),
            ]
        )
        self.assertEqual(len(payload), 3)
        self.assertEqual(payload[0]["content"], [image])
        self.assertEqual(json.loads(payload[2]["content"]), content)


@skipUnless(os.environ.get("DEEPSEEK_TOOL_IMAGE_TEST_URL"), "Start the local DeepSeek tool image Postman simulation")
class DeepSeekToolImageHTTPTests(SimpleTestCase):
    def setUp(self):
        self.model = DeepSeekChatModel(
            model="test-vision-gateway",
            api_key="test-key",
            base_url=os.environ["DEEPSEEK_TOOL_IMAGE_TEST_URL"],
            max_retries=0,
            timeout=10,
        )
        self.images = [image_data_url((2, 3)), image_data_url((4, 5))]
        self.messages = [
            HumanMessage(content="inspect"),
            tool_call_message("call_a", "call_b"),
            image_result("call_a", self.images[0]),
            image_result("call_b", self.images[1]),
        ]

    def _assert_received(self, content):
        received = json.loads(content)
        self.assertEqual(received["roles"], ["user", "assistant", "tool", "tool", "user"])
        self.assertEqual(received["tool_call_ids"], ["call_a", "call_b"])
        self.assertEqual(received["images"], self.images)
        self.assertEqual(received["reasoning"], ["tool reasoning"])

    def test_sync_client_sends_tool_images_as_vision_input(self):
        before = deepcopy([message.model_dump() for message in self.messages])
        self._assert_received(self.model.invoke(self.messages).content)
        self.assertEqual([message.model_dump() for message in self.messages], before)

    async def test_async_stream_sends_tool_images_as_vision_input(self):
        before = deepcopy([message.model_dump() for message in self.messages])
        chunks = [chunk async for chunk in self.model.astream(self.messages)]
        self._assert_received("".join(chunk.content for chunk in chunks))
        self.assertEqual([message.model_dump() for message in self.messages], before)
