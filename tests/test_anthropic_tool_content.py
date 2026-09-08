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
        self.assertFalse(is_anthropic_tool_finish({"stop_reason": "pause_turn"}))

    def test_strips_input_json_delta_and_empty_text(self):
        content = [
            {"type": "text", "text": ""},
            {"type": "tool_use", "id": "toolu_1", "name": "live_price", "input": {}, "index": 1},
            {"type": "input_json_delta", "index": 1, "partial_json": '{"query":'},
            {"type": "input_json_delta", "index": 1, "partial_json": ' "DJI Neo"}'},
        ]
        finalized = finalize_anthropic_assistant_content(content)
        self.assertEqual(len(finalized), 1)
        self.assertEqual(finalized[0]["type"], "tool_use")
        self.assertEqual(finalized[0]["id"], "toolu_1")
        self.assertEqual(finalized[0]["input"], {"query": "DJI Neo"})
        self.assertNotIn("input_json_delta", [block.get("type") for block in finalized])

    def test_fills_tool_use_input_from_tool_calls(self):
        content = [{"type": "tool_use", "id": "toolu_2", "name": "live_price", "input": ""}]
        tool_calls = [{"id": "toolu_2", "name": "live_price", "args": {"query": "in stock"}}]
        finalized = finalize_anthropic_assistant_content(content, tool_calls=tool_calls)
        self.assertEqual(finalized[0]["input"], {"query": "in stock"})

    def test_fills_tool_use_input_from_fragments(self):
        content = [{"type": "tool_use", "id": "toolu_3", "name": "live_price", "input": {}}]
        fragments = {"1": {"id": "toolu_3", "name": "live_price", "arguments": '{"query": "GEL"}'}}
        finalized = finalize_anthropic_assistant_content(content, fragments=fragments)
        self.assertEqual(finalized[0]["input"], {"query": "GEL"})

    def test_fills_tool_use_input_after_deltas_arrive_in_later_chunk(self):
        fragments = {"idx:1": {"id": "toolu_4", "index": 1, "arguments": '{"query": "later"}'}}
        content = [{"type": "tool_use", "id": "toolu_4", "name": "live_price", "input": {}, "index": 1}]
        finalized = finalize_anthropic_assistant_content(content, fragments=fragments)
        self.assertEqual(finalized[0]["input"], {"query": "later"})

    def test_finalizes_combined_stream_chunks_before_replay(self):
        chunks = [
            AIMessageChunk(
                content=[{"type": "tool_use", "id": "toolu_5", "name": "live_price", "input": {}, "index": 0}]
            ),
            AIMessageChunk(content=[{"type": "input_json_delta", "index": 0, "partial_json": '{"q":'}]),
            AIMessageChunk(content=[{"type": "input_json_delta", "index": 0, "partial_json": '"value"}'}]),
        ]
        combined = chunks[0] + chunks[1] + chunks[2]
        finalized = finalize_anthropic_assistant_content(
            combined.content,
            fragments={"idx:0": {"id": "toolu_5", "index": 0, "arguments": '{"q":"value"}'}},
        )
        self.assertEqual(finalized[0]["input"], {"q": "value"})
        self.assertNotIn("input_json_delta", [block.get("type") for block in finalized])

    def test_collect_input_json_deltas_concatenates_partial_json(self):
        content = [
            {"type": "input_json_delta", "index": 0, "partial_json": '{"a":'},
            {"type": "input_json_delta", "index": 0, "input": " 1}"},
        ]
        self.assertEqual(collect_input_json_deltas(content), {0: '{"a": 1}'})

    def test_plain_string_content_is_unchanged(self):
        self.assertEqual(finalize_anthropic_assistant_content("hello"), "hello")

    def test_invalid_tool_input_json_is_rejected(self):
        content = [{"type": "tool_use", "id": "toolu_6", "input": {}, "index": 0}]
        fragments = {"idx:0": {"id": "toolu_6", "index": 0, "arguments": '{"query":'}}
        with self.assertRaises(ValueError):
            finalize_anthropic_assistant_content(content, fragments=fragments)

    def test_delta_without_index_is_rejected(self):
        with self.assertRaises(ValueError):
            collect_input_json_deltas([{"type": "input_json_delta", "partial_json": "{}"}])


if __name__ == "__main__":
    unittest.main()
