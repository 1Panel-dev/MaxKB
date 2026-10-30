"""Regression coverage for the application's LangChain streaming integration."""

import asyncio
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import AsyncMock, MagicMock, patch

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from django.test import SimpleTestCase
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage, ToolMessage
from openai import RateLimitError

from application.workflow.backend import sandbox_shell
from application.workflow.common import CancelledException
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.nodes.ai_chat_node import agent as agent_module
from application.workflow.nodes.llm_node.llm_node import LLMNode
from models_provider.impl.anthropic_model_provider.model.llm import AnthropicChatModel
from models_provider.impl.aws_bedrock_model_provider.model.image import BedrockVLModel
from models_provider.impl.aws_bedrock_model_provider.model.llm import BedrockModel
from models_provider.impl.openai_model_provider.model.llm import OpenAIChatModel


def openai_model(name="fixture-text", **client_options):
    base_url = os.environ.get("LANGCHAIN_COMPAT_TEST_URL", "http://127.0.0.1:0/provider")
    return OpenAIChatModel(
        model=name,
        api_key="test-key",
        base_url=f"{base_url.rstrip('/')}/v1",
        max_retries=0,
        timeout=10,
        stream_usage=True,
        use_responses_api=False,
        profile={"max_input_tokens": 8192},
        **client_options,
    )


def llm_node():
    node = LLMNode.__new__(LLMNode)
    node.data = {}
    node.async_runner = SimpleNamespace(cancel_event=Event())
    node.is_result = True
    node.get_node_id = MagicMock(return_value="llm")
    node.get_node_name = MagicMock(return_value="LLM")
    node._check_cancelled = MagicMock()
    node.write = MagicMock()
    context = {}
    node.write_context = MagicMock(side_effect=context.__setitem__)
    return node, context


class LangChainMessageCompatibilityTests(SimpleTestCase):
    async def test_complete_messages_preserve_text_tools_metadata_and_input(self):
        contents = [
            "你好",
            [
                {"type": "thinking", "thinking": "private"},
                {"type": "text", "text": "你"},
                {"type": "image", "base64": "not-answer"},
                {"type": "text", "text": "好"},
            ],
        ]
        for content in contents:
            with self.subTest(content=content):
                message = AIMessage(
                    content=content,
                    tool_calls=[
                        {"id": "call_sh", "name": "lookup", "args": {"city": "上海"}},
                        {"id": "call_bj", "name": "lookup", "args": {"city": "北京"}},
                    ],
                    additional_kwargs={"reasoning": "思考"},
                    response_metadata={"stop_reason": "tool_use"},
                    usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
                )
                before = message.model_dump()
                closed = Event()

                async def stream(_messages):
                    try:
                        yield message
                    finally:
                        closed.set()

                model = MagicMock()
                model.astream.side_effect = stream
                node, context = llm_node()
                await node._stream_response(model, model, [])

                output = [call.args[0] for call in node.write.call_args_list]
                self.assertEqual("".join(item.content for item in output if isinstance(item, TextContent)), "你好")
                self.assertEqual(context["content"], "你好")
                self.assertEqual(context["reasoning_content"], "思考")
                self.assertEqual(context["reasoning_key"], "reasoning")
                self.assertEqual(context["finish_reason"], "tool_use")
                self.assertEqual(context["usage"], {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15})
                calls = context["tool_calls"]
                self.assertEqual(
                    [(call["original_id"], call["name"], json.loads(call["arguments"])) for call in calls],
                    [("call_sh", "lookup", {"city": "上海"}), ("call_bj", "lookup", {"city": "北京"})],
                )
                cards = [item for item in output if isinstance(item, ToolContent)]
                self.assertEqual([item.id for item in cards], [call["id"] for call in calls])
                self.assertEqual(len({call["id"] for call in calls}), 2)
                self.assertEqual(message.model_dump(), before)
                self.assertTrue(closed.is_set())
                model.get_num_tokens_from_messages.assert_not_called()
                model.get_num_tokens.assert_not_called()

    async def test_text_blocks_reach_stream_and_saved_context_without_tool_payloads(self):
        node, context = llm_node()
        chunks = [
            AIMessageChunk(content=[{"type": "thinking", "thinking": "private"}, {"type": "text", "text": "你"}]),
            AIMessageChunk(
                content=[{"type": "text", "text": "好"}, {"type": "image", "base64": "not-answer"}],
                usage_metadata={"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
            ),
        ]
        before = [chunk.model_dump() for chunk in chunks]

        async def stream(messages):
            for chunk in chunks:
                yield chunk

        model = MagicMock()
        model.astream.side_effect = stream
        await node._stream_response(model, model, [])
        self.assertEqual(context["content"], "你好")
        self.assertEqual(context["usage"]["total_tokens"], 5)
        self.assertEqual("".join(call.args[0].content for call in node.write.call_args_list), "你好")
        self.assertEqual([chunk.model_dump() for chunk in chunks], before)

    def test_shell_output_truncates_by_utf8_bytes_without_broken_characters(self):
        with TemporaryDirectory(prefix="maxkb-shell-compat-") as directory:
            backend = sandbox_shell.SandboxShellBackend(root_dir=directory, max_output_bytes=8)
            with patch.object(sandbox_shell, "_enable_sandbox", False):
                result = backend.execute("printf '中文A你好'")
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.truncated)
        self.assertEqual(result.output.split("\n", 1)[0], "中文A")
        self.assertNotIn("\ufffd", result.output)

    def test_shell_virtual_skill_path_and_exit_status_survive_backend_upgrade(self):
        with TemporaryDirectory(prefix="maxkb-shell-compat-") as directory:
            skill = Path(directory, "skills", "fixture.txt")
            skill.parent.mkdir()
            skill.write_text("技能输出", encoding="utf-8")
            backend = sandbox_shell.SandboxShellBackend(root_dir=directory, virtual_mode=True)
            with patch.object(sandbox_shell, "_enable_sandbox", False):
                result = backend.execute("cat /skills/fixture.txt; exit 7")
        self.assertEqual(result.exit_code, 7)
        self.assertFalse(result.truncated)
        self.assertIn("技能输出", result.output)
        self.assertIn("Exit code: 7", result.output)

    def test_interleaved_tool_arguments_with_empty_ids_merge_once(self):
        model = openai_model()
        parts = [
            (0, "call_sh", "lookup", '{"city":"'),
            (1, "call_bj", "lookup", '{"city":"'),
            (0, "", None, "上海"),
            (1, "", None, "北京"),
            (0, "", None, '"}'),
            (1, "", None, '"}'),
        ]
        full = AIMessageChunk(content="")
        for index, call_id, name, arguments in parts:
            generation = model._convert_chunk_to_generation_chunk(
                {
                    "choices": [
                        {
                            "delta": {
                                "tool_calls": [
                                    {
                                        "index": index,
                                        "id": call_id,
                                        "function": {"name": name, "arguments": arguments},
                                    }
                                ]
                            }
                        }
                    ]
                },
                AIMessageChunk,
                {},
            )
            full += generation.message
        self.assertEqual(full.invalid_tool_calls, [])
        self.assertEqual(
            [(call["id"], call["name"], call["args"]) for call in full.tool_calls],
            [("call_sh", "lookup", {"city": "上海"}), ("call_bj", "lookup", {"city": "北京"})],
        )

    def test_llm_usage_metadata_takes_precedence_over_tokenizer(self):
        node, context = llm_node()
        model = MagicMock()
        message = AIMessageChunk(
            content="你好", usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15}
        )
        node._write_final_context(
            model, [], message, reasoning_content="思考", reasoning_key="reasoning", finish_reason=None, tool_calls=[]
        )
        self.assertEqual(context["usage"], {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15})
        self.assertEqual(context["reasoning_key"], "reasoning")
        self.assertEqual((node.data["message_tokens"], node.data["answer_tokens"]), (12, 3))
        model.get_num_tokens_from_messages.assert_not_called()
        model.get_num_tokens.assert_not_called()

    def test_missing_usage_uses_model_token_count(self):
        node, context = llm_node()
        model = MagicMock()
        model.get_num_tokens_from_messages.return_value = 7
        model.get_num_tokens.return_value = 2
        node._write_final_context(
            model,
            [],
            AIMessageChunk(content="你好"),
            reasoning_content="",
            reasoning_key="",
            finish_reason=None,
            tool_calls=[],
        )
        self.assertEqual(context["usage"], {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9})

    async def test_cancellation_keeps_partial_text_and_closes_stream(self):
        node, context = llm_node()
        closed = Event()

        async def stream(_messages):
            try:
                yield AIMessageChunk(content="已收到")
                node.async_runner.cancel_event.set()
                yield AIMessageChunk(content="不应输出")
            finally:
                closed.set()

        node._check_cancelled.side_effect = [None, CancelledException()]
        model = MagicMock()
        model.astream.side_effect = stream
        with patch("application.workflow.nodes.llm_node.llm_node.count_local_tokens", return_value=(3, 2)) as count:
            with self.assertRaises(CancelledException):
                await node._stream_response(model, model, [])
        self.assertTrue(closed.is_set())
        self.assertEqual(context["content"], "已收到")
        self.assertEqual(context["finish_reason"], "cancelled")
        self.assertEqual(context["usage"]["total_tokens"], 5)
        count.assert_called_once_with([], "已收到")
        model.get_num_tokens.assert_not_called()


@skipUnless(os.environ.get("LANGCHAIN_COMPAT_TEST_URL"), "Start the local LangChain Postman simulation")
class LangChainHTTPCompatibilityTests(SimpleTestCase):
    def setUp(self):
        # Each test owns its connections and event loop, just as the production
        # AsyncRunner keeps model connections on one loop across agent rounds.
        self.runner = asyncio.Runner()
        self.addCleanup(self.runner.close)
        self.http_client = httpx.Client()
        self.addCleanup(self.http_client.close)
        self.http_async_client = httpx.AsyncClient()
        self.addCleanup(lambda: self.runner.run(self.http_async_client.aclose()))

    def model(self, name="fixture-text"):
        return openai_model(name, http_client=self.http_client, http_async_client=self.http_async_client)

    def test_sync_invoke_keeps_provider_token_counts(self):
        model = self.model()
        message = model.invoke([HumanMessage(content="hello")])
        self.assertEqual(message.content, "你好")
        self.assertEqual(model.get_num_tokens_from_messages([]), 12)
        self.assertEqual(model.get_num_tokens("你好"), 3)

    def test_sync_stream_keeps_reasoning_and_trailing_usage(self):
        model = self.model()
        chunks = list(model.stream([HumanMessage(content="hello")]))
        self.assertEqual("".join(chunk.content for chunk in chunks), "你好")
        self.assertEqual("".join(chunk.additional_kwargs.get("reasoning_content", "") for chunk in chunks), "思考")
        full = sum(chunks[1:], chunks[0])
        self.assertEqual(full.usage_metadata["input_tokens"], 12)
        self.assertEqual(full.usage_metadata["input_token_details"]["cache_read"], 4)
        self.assertEqual(full.usage_metadata["output_token_details"]["reasoning"], 1)
        self.assertEqual(model.get_num_tokens_from_messages([]), 12)
        self.assertEqual(model.get_num_tokens("你好"), 3)

    def test_async_stream_reaches_llm_node_with_exact_usage(self):
        model = self.model()
        node, context = llm_node()
        self.runner.run(node._stream_response(model, model, [HumanMessage(content="hello")]))
        output = [call.args[0] for call in node.write.call_args_list]
        self.assertEqual("".join(item.content for item in output if isinstance(item, TextContent)), "你好")
        self.assertEqual("".join(item.content for item in output if isinstance(item, ReasoningContent)), "思考")
        self.assertEqual(context["content"], "你好")
        self.assertEqual(context["reasoning_content"], "思考")
        self.assertEqual(context["usage"], {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15})
        self.assertEqual(context["finish_reason"], "stop")

    def test_async_parallel_tool_calls_reach_llm_context(self):
        model = self.model("fixture-tools")

        def lookup(city: str) -> str:
            """Look up a city."""
            return city

        node, context = llm_node()
        self.runner.run(node._stream_response(model.bind_tools([lookup]), model, [HumanMessage(content="lookup")]))
        calls = context["tool_calls"]
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            [(call["original_id"], call["name"], json.loads(call["arguments"])) for call in calls],
            [("call_sh", "lookup", {"city": "上海"}), ("call_bj", "lookup", {"city": "北京"})],
        )
        self.assertEqual(context["finish_reason"], "tool_calls")
        self.assertEqual(context["usage"], {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18})

    def test_real_deep_agent_executes_each_tool_once_and_continues(self):
        model = self.model("fixture-agent")
        executed, events, errors = [], [], []

        def lookup(city: str) -> str:
            """Look up a city."""
            executed.append(city)
            return f"{city}:晴"

        with (
            TemporaryDirectory(prefix="maxkb-agent-compat-") as directory,
            patch.object(agent_module, "init_skills", new=AsyncMock()),
            patch.object(
                agent_module,
                "MultiServerMCPClient",
                return_value=SimpleNamespace(get_tools=AsyncMock(return_value=[])),
            ),
        ):
            agent_module.create_agent(
                model,
                "Use lookup for both cities, then answer.",
                [HumanMessage(content="上海和北京的天气")],
                "{}",
                SimpleNamespace(on_next=events.append, on_complete=errors.append),
                chat_id=directory,
                extra_tools=[lookup],
                async_runner=SimpleNamespace(run_async=lambda fn: self.runner.run(fn())),
            )
        self.assertEqual(errors, [None])
        self.assertCountEqual(executed, ["上海", "北京"])
        results = [event for event in events if isinstance(event, ToolMessage)]
        self.assertEqual(
            {event.tool_call_id: event.content for event in results}, {"call_sh": "上海:晴", "call_bj": "北京:晴"}
        )
        self.assertEqual("".join(event.content for event in events if isinstance(event, AIMessageChunk)), "查询完成")
        # Preserve the adapter's existing last-generation accounting, not a sum of agent rounds.
        self.assertEqual(model.get_num_tokens_from_messages([]), 20)
        self.assertEqual(model.get_num_tokens("查询完成"), 4)

    def test_agent_recursion_limit_reports_error_once_and_cleans_workspace(self):
        executed, errors = [], []

        def lookup(city: str) -> str:
            """Look up a city."""
            executed.append(city)
            return city

        with (
            TemporaryDirectory(prefix="maxkb-agent-limit-") as directory,
            patch.object(agent_module, "init_skills", new=AsyncMock()),
            patch.object(agent_module.CONFIG, "get", return_value="1"),
            patch.object(
                agent_module,
                "MultiServerMCPClient",
                return_value=SimpleNamespace(get_tools=AsyncMock(return_value=[])),
            ),
        ):
            agent_module.create_agent(
                self.model("fixture-agent"),
                "Use lookup.",
                [HumanMessage(content="上海和北京")],
                "{}",
                SimpleNamespace(on_next=lambda message: None, on_complete=errors.append),
                chat_id=directory,
                extra_tools=[lookup],
                async_runner=SimpleNamespace(run_async=lambda fn: self.runner.run(fn())),
            )
            self.assertFalse(Path(directory).exists())
        self.assertEqual(executed, [])
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RuntimeError)
        self.assertIn("GraphRecursionError", str(errors[0]))

    def test_anthropic_tool_json_and_cached_token_counts(self):
        model = AnthropicChatModel(
            model="fixture-claude",
            api_key="test-key",
            base_url=os.environ["LANGCHAIN_COMPAT_TEST_URL"].rstrip("/"),
            max_tokens=64,
            max_retries=0,
            timeout=10,
        )

        def lookup(city: str) -> str:
            """Look up a city."""
            return city

        async def collect():
            try:
                return [chunk async for chunk in model.bind_tools([lookup]).astream([HumanMessage(content="lookup")])]
            finally:
                await model._async_client.close()

        chunks = self.runner.run(collect())
        full = sum(chunks[1:], chunks[0])
        self.assertEqual(full.invalid_tool_calls, [])
        self.assertEqual([(call["id"], call["args"]) for call in full.tool_calls], [("toolu_city", {"city": "上海"})])
        self.assertEqual(full.usage_metadata["input_tokens"], 15)
        self.assertEqual(full.usage_metadata["output_tokens"], 4)
        self.assertEqual(full.usage_metadata["total_tokens"], 19)
        self.assertEqual(full.usage_metadata["input_token_details"], {"cache_creation": 2, "cache_read": 3})
        node, context = llm_node()
        node._write_final_context(
            model, [], full, reasoning_content="", reasoning_key="", finish_reason=None, tool_calls=[]
        )
        self.assertEqual(context["usage"], {"prompt_tokens": 15, "completion_tokens": 4, "total_tokens": 19})

    def test_provider_error_reaches_caller_and_records_failed_finish(self):
        model = self.model("fixture-error")
        node, context = llm_node()
        with (
            patch.object(OpenAIChatModel, "get_num_tokens_from_messages", return_value=0),
            patch.object(OpenAIChatModel, "get_num_tokens", return_value=0),
        ):
            with self.assertRaises(RateLimitError):
                self.runner.run(node._stream_response(model, model, [HumanMessage(content="hello")]))
        self.assertEqual(context["finish_reason"], "error")
        self.assertEqual(context["content"], "")


@skipUnless(os.environ.get("LANGCHAIN_COMPAT_TEST_URL"), "Start the local LangChain Postman simulation")
class BedrockHTTPCompatibilityTests(SimpleTestCase):
    def setUp(self):
        self.runner = asyncio.Runner()
        self.addCleanup(self.runner.close)
        options = {
            "region_name": "us-east-1",
            "aws_access_key_id": "test-access-key",
            "aws_secret_access_key": "test-secret-key",
            "endpoint_url": os.environ["LANGCHAIN_COMPAT_TEST_URL"].rstrip("/"),
            "config": Config(retries={"max_attempts": 0}, connect_timeout=5, read_timeout=5, proxies={}),
        }
        session = boto3.Session()
        self.client = session.client("bedrock-runtime", **options)
        self.control_client = session.client("bedrock", **options)
        self.addCleanup(self.client.close)
        self.addCleanup(self.control_client.close)

    def model(self, model_class=BedrockModel, *, streaming=False):
        return model_class(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name="us-east-1",
            credentials_profile_name=None,
            client=self.client,
            bedrock_client=self.control_client,
            model_kwargs={"max_tokens": 64},
            streaming=streaming,
        )

    def assert_usage(self, message):
        self.assertEqual(message.usage_metadata["input_tokens"], 15)
        self.assertEqual(message.usage_metadata["output_tokens"], 4)
        self.assertEqual(message.usage_metadata["total_tokens"], 19)
        self.assertEqual(message.usage_metadata["input_token_details"], {"cache_read": 3, "cache_creation": 2})

    def test_invoke_and_llm_context_include_cached_tokens_once(self):
        model = self.model()
        message = model.invoke([HumanMessage(content="hello")])
        self.assertEqual(message.content, "你好")
        self.assert_usage(message)
        node, context = llm_node()
        node._write_final_context(
            model, [], message, reasoning_content="", reasoning_key="", finish_reason=None, tool_calls=[]
        )
        self.assertEqual(context["usage"], {"prompt_tokens": 15, "completion_tokens": 4, "total_tokens": 19})

    def test_binary_stream_reaches_async_llm_node_with_complete_usage(self):
        model = self.model(streaming=True)
        node, context = llm_node()
        self.runner.run(node._stream_response(model, model, [HumanMessage(content="hello")]))
        self.assertEqual(context["content"], "你好")
        self.assertEqual(context["usage"], {"prompt_tokens": 15, "completion_tokens": 4, "total_tokens": 19})
        self.assertEqual("".join(call.args[0].content for call in node.write.call_args_list), "你好")

    def test_streamed_tool_arguments_and_result_round_trip(self):
        model = self.model(streaming=True)

        def lookup(city: str) -> str:
            """Look up a city."""
            return f"{city}:晴"

        bound = model.bind_tools([lookup])
        messages = [HumanMessage(content="lookup")]
        chunks = list(bound.stream(messages))
        full = sum(chunks[1:], chunks[0])
        self.assertEqual(full.invalid_tool_calls, [])
        self.assertEqual(
            [(call["id"], call["args"]) for call in full.tool_calls], [("toolu_bedrock", {"city": "上海"})]
        )
        self.assert_usage(full)
        reply = (
            self.model()
            .bind_tools([lookup])
            .invoke([*messages, full, ToolMessage(content="上海:晴", tool_call_id="toolu_bedrock")])
        )
        self.assertEqual(reply.content, "查询完成")
        self.assert_usage(reply)

    def test_streamed_tool_arguments_reach_llm_context(self):
        model = self.model(streaming=True)

        def lookup(city: str) -> str:
            """Look up a city."""
            return city

        node, context = llm_node()
        self.runner.run(node._stream_response(model.bind_tools([lookup]), model, [HumanMessage(content="lookup")]))
        calls = context["tool_calls"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["original_id"], "toolu_bedrock")
        self.assertEqual(json.loads(calls[0]["arguments"]), {"city": "上海"})
        self.assertEqual(context["usage"]["total_tokens"], 19)

    def test_nonstream_fallback_preserves_text_tools_and_usage(self):
        model = self.model()

        def lookup(city: str) -> str:
            """Look up a city."""
            return city

        for with_tools in (False, True):
            with self.subTest(with_tools=with_tools):
                node, context = llm_node()
                bound = model.bind_tools([lookup]) if with_tools else model
                self.runner.run(node._stream_response(bound, model, [HumanMessage(content="hello")]))
                self.assertEqual(context["content"], "" if with_tools else "你好")
                self.assertEqual(context["finish_reason"], "tool_use" if with_tools else "end_turn")
                self.assertEqual(context["usage"]["total_tokens"], 19)
                self.assertEqual(len(context["tool_calls"]), int(with_tools))
                if with_tools:
                    self.assertEqual(context["tool_calls"][0]["original_id"], "toolu_bedrock")
                    self.assertEqual(json.loads(context["tool_calls"][0]["arguments"]), {"city": "上海"})

    def test_vision_adapter_preserves_inline_image_and_usage(self):
        # A synthetic one-pixel PNG; the fixture checks the encoded image request.
        image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aB9sAAAAASUVORK5CYII="
        message = self.model(BedrockVLModel).invoke(
            [
                SystemMessage(content="fixture-vision"),
                HumanMessage(
                    content=[
                        {"type": "text", "text": "describe"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}},
                    ]
                ),
            ]
        )
        self.assertEqual(message.content, "你好")
        self.assert_usage(message)

    def test_rate_limit_error_reaches_caller(self):
        with self.assertRaises(ClientError) as caught:
            self.model().invoke([SystemMessage(content="fixture-error"), HumanMessage(content="hello")])
        self.assertEqual(caught.exception.response["Error"]["Code"], "ThrottlingException")
