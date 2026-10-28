import sys
import unittest
from pathlib import Path

from langchain_core.messages import AIMessageChunk

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps"))

from application.flow.anthropic_tool_content import (
    collect_input_json_deltas,
    finalize_anthropic_assistant_content,
    is_anthropic_tool_finish,
)


class AnthropicToolContentTests(unittest.TestCase):
    def test_finish_detects_anthropic_stop_reason(self):
        self.assertTrue(is_anthropic_tool_finish({"stop_reason": "tool_use"}))
        self.assertTrue(is_anthropic_tool_finish({"finish_reason": "tool_calls"}))
        self.assertTrue(is_anthropic_tool_finish({}, chunk_position="last"))
        self.assertFalse(is_anthropic_tool_finish({"stop_reason": "end_turn"}))

    def test_strips_deltas_and_fills_tool_input(self):
        content = [
            {"type": "text", "text": ""},
            {"type": "tool_use", "id": "toolu_1", "name": "lookup", "input": {}, "index": 1},
            {"type": "input_json_delta", "index": 1, "partial_json": '{"query":'},
            {"type": "input_json_delta", "index": 1, "partial_json": ' "MaxKB"}'},
        ]

        finalized = finalize_anthropic_assistant_content(content)

        self.assertEqual(
            finalized,
            [{"type": "tool_use", "id": "toolu_1", "name": "lookup", "input": {"query": "MaxKB"}, "index": 1}],
        )

    def test_fills_tool_use_input_from_tool_calls(self):
        content = [{"type": "tool_use", "id": "toolu_2", "name": "lookup", "input": ""}]
        tool_calls = [{"id": "toolu_2", "name": "lookup", "args": {"query": "value"}}]

        finalized = finalize_anthropic_assistant_content(content, tool_calls=tool_calls)

        self.assertEqual(finalized[0]["input"], {"query": "value"})

    def test_collect_input_json_deltas_concatenates_fragments(self):
        content = [
            {"type": "input_json_delta", "index": 0, "partial_json": '{"a":'},
            {"type": "input_json_delta", "index": 0, "partial_json": " 1}"},
        ]

        self.assertEqual(collect_input_json_deltas(content), {0: '{"a": 1}'})

    def test_finalizes_langchain_merged_stream(self):
        chunks = [
            AIMessageChunk(content=[{"type": "tool_use", "id": "toolu_3", "name": "lookup", "input": {}, "index": 0}]),
            AIMessageChunk(content=[{"type": "input_json_delta", "index": 0, "partial_json": '{"q":'}]),
            AIMessageChunk(content=[{"type": "input_json_delta", "index": 0, "partial_json": '"v"}'}]),
        ]
        merged = chunks[0] + chunks[1] + chunks[2]

        finalized = finalize_anthropic_assistant_content(
            merged.content,
            fragments={"idx:0": {"id": "toolu_3", "index": 0, "arguments": '{"q":"v"}'}},
        )

        self.assertEqual(finalized[0]["input"], {"q": "v"})
        self.assertNotIn("partial_json", finalized[0])


if __name__ == "__main__":
    unittest.main()
