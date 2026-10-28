import asyncio
import json
from copy import deepcopy
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from django.test import SimpleTestCase
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from application.workflow.common import WorkflowType
from application.workflow.message.aggregator import AggregationManager
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.nodes.ai_chat_node import agent as agent_module
from application.workflow.nodes.ai_chat_node.ai_chat_node import AIChatNode
from application.workflow.status import Status


class AIChatToolOutputTests(SimpleTestCase):
    def _run_messages(self, messages=(), *, enabled=True, emit=None):
        node = AIChatNode.__new__(AIChatNode)
        node.async_runner = MagicMock()
        node.get_workflow_parameters = MagicMock(return_value={"application_id": "application"})
        node.get_node_id = MagicMock(return_value="ai")
        node.get_node_name = MagicMock(return_value="AI")
        node._check_cancelled = MagicMock()
        node._write_final_context = MagicMock()
        node.write = MagicMock()

        def run_agent(_model, _system, _messages, _servers, callback, *_args, **_kwargs):
            if emit:
                emit(callback.on_next)
            else:
                for message in messages:
                    callback.on_next(message)
            callback.on_complete(None)

        module = "application.workflow.nodes.ai_chat_node.ai_chat_node"
        with (
            patch(f"{module}.get_tool_tools", return_value=[]),
            patch(f"{module}.get_application_tools", return_value=[]),
            patch(f"{module}.get_mcp_servers", return_value={}),
            patch(f"{module}.ToolExecutor"),
            patch(f"{module}.create_agent", side_effect=run_agent),
        ):
            handled = node._handle_mcp(
                mcp_source="custom",
                mcp_servers="{}",
                mcp_tool_id=None,
                mcp_tool_ids=[],
                tool_ids=[],
                application_ids=[],
                skill_tool_ids=["skill"],
                mcp_output_enable=enabled,
                chat_model=MagicMock(),
                system_prompt=SystemMessage(content="system"),
                message_list=[],
                question=HumanMessage(content="question"),
                chat_id="chat",
                workspace_id="workspace",
                workflow_type=WorkflowType.APPLICATION,
                is_result=True,
            )
        self.assertTrue(handled)
        return node, [call.args[0] for call in node.write.call_args_list]

    def _display(self, content):
        message = ToolMessage(content=content, tool_call_id="call_tool", name="tool")
        before = deepcopy(message.model_dump())
        node, output = self._run_messages([message])
        cards = [item for item in output if isinstance(item, ToolContent)]
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].status, Status.SUCCESS)
        self.assertIsInstance(cards[0].content, str)
        self.assertEqual(message.model_dump(), before)
        self.assertEqual(node._write_final_context.call_args.args[3], "")
        return cards[0]

    def test_plain_text_and_json_results_remain_strings_in_cards(self):
        cases = [
            ("plain result", "plain result"),
            ('"JSON string"', "JSON string"),
            ('{"answer": "你好", "tool_id": "business-id"}', '{"answer": "你好", "tool_id": "business-id"}'),
            ('[1, "two", null]', '[1, "two", null]'),
            ("true", "true"),
            ("null", "null"),
            ("42", "42"),
            ("", ""),
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                self.assertEqual(self._display(content).content, expected)

    def test_single_text_block_is_unwrapped_without_requiring_json(self):
        for text, expected in [("plain text", "plain text"), ('{"answer":42}', '{"answer": 42}'), ("", "")]:
            with self.subTest(text=text):
                self.assertEqual(self._display([{"type": "text", "text": text}]).content, expected)

    def test_all_blocks_are_preserved_in_order(self):
        content = [
            {"type": "text", "text": '{"first":1}'},
            {"type": "image", "base64": "image-payload", "mime_type": "image/png"},
            {"type": "text", "text": "plain text"},
            {"type": "text", "text": '{"last":2}'},
        ]
        self.assertEqual(
            json.loads(self._display(content).content),
            [
                {"first": 1},
                {"type": "image", "base64": "[base64 omitted]", "mime_type": "image/png"},
                "plain text",
                {"last": 2},
            ],
        )

    def test_image_first_does_not_discard_later_text(self):
        content = [
            {"type": "image", "data": "image-payload", "mimeType": "image/png"},
            {"type": "text", "text": "caption"},
        ]
        self.assertEqual(
            json.loads(self._display(content).content),
            [{"type": "image", "data": "[base64 omitted]", "mimeType": "image/png"}, "caption"],
        )

    def test_plain_text_before_image_does_not_fall_back_to_raw_base64(self):
        content = [{"type": "text", "text": "not JSON"}, {"type": "image", "base64": "image-payload"}]
        self.assertEqual(
            json.loads(self._display(content).content),
            ["not JSON", {"type": "image", "base64": "[base64 omitted]"}],
        )

    def test_media_payloads_are_omitted_but_metadata_and_urls_are_preserved(self):
        cases = [
            (
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,payload"}},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,[omitted]"}},
            ),
            (
                {"type": "input_audio", "input_audio": {"data": "payload", "format": "wav"}},
                {"type": "input_audio", "input_audio": {"data": "[base64 omitted]", "format": "wav"}},
            ),
            (
                {"type": "resource", "resource": {"blob": "payload", "mimeType": "application/pdf"}},
                {"type": "resource", "resource": {"blob": "[base64 omitted]", "mimeType": "application/pdf"}},
            ),
            (
                {"type": "file", "source": {"type": "base64", "data": "payload"}, "name": "report.pdf"},
                {"type": "file", "source": {"type": "base64", "data": "[base64 omitted]"}, "name": "report.pdf"},
            ),
            (
                {"type": "video", "url": "data:video/mp4;base64,payload"},
                {"type": "video", "url": "data:video/mp4;base64,[omitted]"},
            ),
            (
                {"type": "image", "url": "https://example.com/image.png"},
                {"type": "image", "url": "https://example.com/image.png"},
            ),
        ]
        for content, expected in cases:
            with self.subTest(media_type=content["type"]):
                self.assertEqual(json.loads(self._display([content]).content), expected)

    def test_media_inside_json_text_is_sanitized_without_changing_business_fields(self):
        result = {
            "data": "business-data",
            "base64": "business-value",
            "blob": "business-blob",
            "tool_id": "business-id",
            "image": {"type": "image", "base64": "image-payload"},
        }
        expected = deepcopy(result)
        expected["image"]["base64"] = "[base64 omitted]"
        self.assertEqual(json.loads(self._display([{"type": "text", "text": json.dumps(result)}]).content), expected)

    def test_empty_content_list_is_preserved(self):
        self.assertEqual(json.loads(self._display([]).content), [])

    def test_display_name_does_not_mutate_the_original_message(self):
        tool_call = AIMessageChunk(
            content="",
            tool_call_chunks=[{"name": "display-tool", "args": "{}", "id": "call_tool", "index": 0}],
        )
        message = ToolMessage(
            content=[{"type": "text", "text": "result"}],
            name="original-tool",
            tool_call_id="call_tool",
            artifact={"original": "record"},
        )
        before = deepcopy(message.model_dump())
        _, output = self._run_messages([tool_call, message])
        cards = [item for item in output if isinstance(item, ToolContent)]
        self.assertEqual(message.model_dump(), before)
        self.assertEqual(cards[-1].name, "display-tool")
        self.assertEqual(cards[0].id, cards[-1].id)

    def test_result_without_call_chunk_uses_message_name(self):
        self.assertEqual(self._display("result").name, "tool")

    def test_internal_summary_events_never_reach_answer_or_tool_cards(self):
        ordinary = AIMessageChunk(content="summary is an ordinary word")
        events = [
            (AIMessageChunk(content="internal summary"), {"lc_source": "summarization", "langgraph_node": "model"}),
            (
                AIMessageChunk(
                    content="",
                    tool_call_chunks=[{"name": "hidden", "args": "{}", "id": "call_hidden", "index": 0}],
                ),
                {"lc_source": "summarization", "langgraph_node": "model"},
            ),
            (ordinary, {"langgraph_node": "model"}),
            (AIMessageChunk(content="; done"), {}),
        ]

        def emit(on_next):
            async def stream(*args, **kwargs):
                for event in events:
                    yield event

            def on_complete(error):
                if error:
                    raise error

            with (
                TemporaryDirectory(prefix="maxkb-summary-test-") as directory,
                patch.object(agent_module, "init_skills", new=AsyncMock()),
                patch.object(
                    agent_module,
                    "MultiServerMCPClient",
                    return_value=SimpleNamespace(get_tools=AsyncMock(return_value=[])),
                ),
                patch.object(agent_module, "SandboxShellBackend"),
                patch.object(agent_module, "create_deep_agent", return_value=SimpleNamespace(astream=stream)),
            ):
                agent_module.create_agent(
                    MagicMock(),
                    "system",
                    [],
                    "{}",
                    SimpleNamespace(on_next=on_next, on_complete=on_complete),
                    chat_id=directory,
                    async_runner=SimpleNamespace(run_async=lambda fn: asyncio.run(fn())),
                )

        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                node, output = self._run_messages(enabled=enabled, emit=emit)
                self.assertEqual(node._write_final_context.call_args.args[3], ordinary.content + "; done")
                self.assertEqual("".join(item.content for item in output), ordinary.content + "; done")
                self.assertFalse(any(isinstance(item, ToolContent) for item in output))

    def test_fallback_tool_calls_preserve_arguments_names_and_original_messages(self):
        sources = [
            {"tool_calls": [{"name": "fallback", "args": {"q": "你好"}, "id": "call_tool"}]},
            {"invalid_tool_calls": [{"name": "fallback", "args": '{"q": "你好"}', "id": "call_tool"}]},
            {
                "additional_kwargs": {
                    "tool_calls": [{"id": "call_tool", "function": {"name": "fallback", "arguments": '{"q": "你好"}'}}]
                }
            },
        ]
        for source in sources:
            with self.subTest(source=source):
                # Exercise providers that supply complete calls without incremental chunks.
                call = AIMessageChunk(content="").model_copy(update={**source, "tool_call_chunks": []})
                before = deepcopy(call.model_dump())
                result = ToolMessage(content="ok", tool_call_id="call_tool")
                _, output = self._run_messages([call, call, result])
                cards = [item for item in output if isinstance(item, ToolContent)]
                self.assertEqual(len(cards), 2)
                self.assertEqual(cards[0].status, Status.RUNNING)
                self.assertEqual(cards[0].name, "fallback")
                self.assertIsInstance(cards[0].arguments, str)
                self.assertEqual(json.loads(cards[0].arguments), {"q": "你好"})
                self.assertEqual(cards[-1].name, "fallback")
                aggregation = AggregationManager()
                for card in cards:
                    aggregation.aggregate(card)
                self.assertEqual(json.loads(aggregation.get_contents()[0]["arguments"]), {"q": "你好"})
                self.assertEqual(call.model_dump(), before)
                self.assertIsNone(result.name)

    def test_fallback_without_arguments_is_an_empty_object(self):
        call = AIMessageChunk(content="").model_copy(
            update={"tool_calls": [{"name": "tool", "args": None, "id": "call_tool"}], "tool_call_chunks": []}
        )
        _, output = self._run_messages([call])
        cards = [item for item in output if isinstance(item, ToolContent)]
        self.assertEqual(len(cards), 1)
        self.assertEqual(json.loads(cards[0].arguments), {})

    def test_fallback_does_not_repeat_previously_streamed_arguments(self):
        streamed = AIMessageChunk(
            content="", tool_call_chunks=[{"name": "tool", "args": '{"q":1}', "id": "call_tool", "index": 0}]
        )
        fallback = AIMessageChunk(content="").model_copy(
            update={"tool_calls": [{"name": "tool", "args": {"q": 1}, "id": "call_tool"}], "tool_call_chunks": []}
        )
        _, output = self._run_messages([streamed, fallback, ToolMessage(content="ok", tool_call_id="call_tool")])
        cards = [item for item in output if isinstance(item, ToolContent)]
        self.assertEqual(len(cards), 2)
        self.assertEqual("".join(card.arguments for card in cards), '{"q":1}')

    def test_disabled_display_ignores_tool_results_and_preserves_model_answer(self):
        for content in [
            "hidden tool output",
            [{"type": "text", "text": "hidden"}],
            [],
            [{"type": "image", "data": "payload"}],
        ]:
            with self.subTest(content=content):
                message = ToolMessage(content=content, name="tool", tool_call_id="call_tool")
                before = deepcopy(message.model_dump())
                node, output = self._run_messages(
                    [
                        AIMessageChunk(
                            content="before ",
                            tool_call_chunks=[{"name": "tool", "args": "{}", "id": "call_tool", "index": 0}],
                        ),
                        message,
                        AIMessageChunk(content="after"),
                    ],
                    enabled=False,
                )
                self.assertFalse(any(isinstance(item, ToolContent) for item in output))
                self.assertEqual(
                    "".join(item.content for item in output if isinstance(item, TextContent)), "before after"
                )
                self.assertEqual(node._write_final_context.call_args.args[3], "before after")
                self.assertEqual(message.model_dump(), before)

    def test_stream_display_does_not_change_subsequent_graph_state(self):
        message = ToolMessage(
            id="tool-message",
            content=[{"type": "text", "text": '{"answer":42}'}, {"type": "image", "base64": "image-payload"}],
            tool_call_id="call_tool",
            name="original-tool",
        )
        before = deepcopy(message.model_dump())

        def emit(on_next):
            on_next(
                AIMessageChunk(
                    content="",
                    tool_call_chunks=[{"name": "display-tool", "args": "{}", "id": "call_tool", "index": 0}],
                )
            )

            async def run_graph():
                async def tools(state):
                    return {"messages": [message]}

                async def next_model_input(state):
                    self.assertIs(state["messages"][-1], message)
                    self.assertEqual(state["messages"][-1].model_dump(), before)
                    return {}

                builder = StateGraph(MessagesState)
                builder.add_node("tools", tools)
                builder.add_node("next_model_input", next_model_input)
                builder.add_edge(START, "tools")
                builder.add_edge("tools", "next_model_input")
                builder.add_edge("next_model_input", END)
                graph = builder.compile(checkpointer=MemorySaver())
                async for chunk, _ in graph.astream(
                    {"messages": []}, config={"configurable": {"thread_id": "test"}}, stream_mode="messages"
                ):
                    if isinstance(chunk, ToolMessage):
                        self.assertIs(chunk, message)
                        on_next(chunk)

            asyncio.run(run_graph())

        _, output = self._run_messages(emit=emit)
        cards = [item for item in output if isinstance(item, ToolContent)]
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[-1].status, Status.SUCCESS)
        self.assertEqual(cards[-1].name, "display-tool")
        self.assertNotIn("image-payload", cards[-1].content)
