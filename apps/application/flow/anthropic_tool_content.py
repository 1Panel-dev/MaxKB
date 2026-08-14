# coding=utf-8
"""Assemble Anthropic streamed tool_use blocks before they are replayed.

Anthropic streams tool arguments as `input_json_delta` events. Those deltas are
valid on the wire, but they are not legal `messages[].content` block types.
Replaying them on the next turn yields:

    Input tag 'input_json_delta' found using 'type' does not match any of the expected tags

Empty `text` blocks from the same stream also fail with:

    messages: text content blocks must be non-empty
"""

from __future__ import annotations

import json

ANTHROPIC_TOOL_STOP_REASONS = ("tool_use", "end_turn")
_STREAM_DELTA_TYPES = {"input_json_delta"}


def is_anthropic_tool_finish(response_metadata, chunk_position=None) -> bool:
    """True when this chunk closes an Anthropic (or OpenAI-mapped) tool turn."""
    meta = response_metadata or {}
    if meta.get("finish_reason") == "tool_calls":
        return True
    if meta.get("stop_reason") in ANTHROPIC_TOOL_STOP_REASONS:
        return True
    return chunk_position == "last"


def collect_input_json_deltas(content) -> dict:
    """Concatenate `input_json_delta` fragments keyed by content-block index."""
    collected = {}
    if not isinstance(content, list):
        return collected
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "input_json_delta":
            continue
        index = block.get("index")
        if index is None:
            continue
        piece = block.get("partial_json")
        if piece is None:
            piece = block.get("input") or ""
        if not isinstance(piece, str):
            piece = json.dumps(piece, ensure_ascii=False) if piece else ""
        collected[index] = collected.get(index, "") + piece
    return collected


def _parse_tool_input(raw):
    if raw is None or raw == "":
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if not isinstance(raw, str):
        return None
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, (dict, list)) else None


def _input_from_tool_calls(block, tool_calls):
    block_id = block.get("id")
    for tool_call in tool_calls or []:
        if not isinstance(tool_call, dict):
            continue
        if block_id and tool_call.get("id") == block_id:
            return _parse_tool_input(tool_call.get("args") or tool_call.get("arguments"))
        if block.get("index") is not None and tool_call.get("index") == block.get("index"):
            return _parse_tool_input(tool_call.get("args") or tool_call.get("arguments"))
    return None


def _input_from_fragments(block, fragments):
    if not fragments:
        return None
    block_id = block.get("id")
    block_index = block.get("index")
    for entry in fragments.values():
        if not isinstance(entry, dict):
            continue
        if block_id and entry.get("id") == block_id:
            return _parse_tool_input(entry.get("arguments"))
        if block_index is not None and entry.get("index") == block_index:
            return _parse_tool_input(entry.get("arguments"))
    return None


def _is_empty_text_block(block) -> bool:
    if not isinstance(block, dict):
        return False
    if block.get("type") not in ("text", "text_delta"):
        return False
    return not str(block.get("text") or "").strip()


def finalize_anthropic_assistant_content(content, tool_calls=None, fragments=None):
    """Drop streamed deltas and fill completed `tool_use.input` values.

    Non-list content (plain strings) is returned unchanged.
    """
    if not isinstance(content, list):
        return content

    json_by_index = collect_input_json_deltas(content)
    finalized = []
    for block in content:
        if not isinstance(block, dict):
            finalized.append(block)
            continue
        if block.get("type") in _STREAM_DELTA_TYPES:
            continue
        if _is_empty_text_block(block):
            continue
        if block.get("type") == "tool_use":
            new_block = dict(block)
            filled = (
                _input_from_fragments(new_block, fragments)
                or _input_from_tool_calls(new_block, tool_calls)
                or _parse_tool_input(json_by_index.get(new_block.get("index")))
            )
            current = new_block.get("input")
            if filled is not None and (current in (None, "", {}, []) or not current):
                new_block["input"] = filled
            elif current == "":
                new_block["input"] = {}
            finalized.append(new_block)
            continue
        finalized.append(block)
    return finalized
