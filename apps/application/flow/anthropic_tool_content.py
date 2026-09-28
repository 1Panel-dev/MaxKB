# coding=utf-8
"""Normalize Anthropic streamed tool content before message replay."""

import json

ANTHROPIC_TOOL_STOP_REASONS = {"tool_use"}


def is_anthropic_tool_finish(response_metadata, chunk_position=None):
    metadata = response_metadata or {}
    return (
        metadata.get("finish_reason") == "tool_calls"
        or metadata.get("stop_reason") in ANTHROPIC_TOOL_STOP_REASONS
        or chunk_position == "last"
    )


def collect_input_json_deltas(content):
    collected = {}
    if not isinstance(content, list):
        return collected
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "input_json_delta":
            continue
        index = block.get("index")
        if index is None:
            raise ValueError("Anthropic input_json_delta is missing its content-block index")
        fragment = block.get("partial_json", block.get("input", ""))
        if not isinstance(fragment, str):
            fragment = json.dumps(fragment, ensure_ascii=False)
        collected[index] = collected.get(index, "") + fragment
    return collected


def _parse_tool_input(value):
    if isinstance(value, (dict, list)):
        return value
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError("Invalid Anthropic tool input JSON") from error
    if not isinstance(parsed, (dict, list)):
        raise ValueError("Anthropic tool input must be an object or array")
    return parsed


def _input_from_fragments(block, fragments):
    if not fragments:
        return None
    for fragment in fragments.values():
        if not isinstance(fragment, dict):
            continue
        if block.get("id") and fragment.get("id") == block["id"]:
            return _parse_tool_input(fragment.get("arguments"))
        if block.get("index") is not None and fragment.get("index") == block["index"]:
            return _parse_tool_input(fragment.get("arguments"))
    return None


def _input_from_tool_calls(block, tool_calls):
    for tool_call in tool_calls or []:
        if not isinstance(tool_call, dict):
            continue
        if block.get("id") and tool_call.get("id") == block["id"]:
            return _parse_tool_input(tool_call.get("args") or tool_call.get("arguments"))
        if block.get("index") is not None and tool_call.get("index") == block["index"]:
            return _parse_tool_input(tool_call.get("args") or tool_call.get("arguments"))
    return None


def finalize_anthropic_assistant_content(content, tool_calls=None, fragments=None):
    if not isinstance(content, list):
        return content

    json_by_index = collect_input_json_deltas(content)
    finalized = []
    for block in content:
        if not isinstance(block, dict):
            finalized.append(block)
            continue
        block_type = block.get("type")
        if block_type == "input_json_delta":
            continue
        if block_type in ("text", "text_delta") and not str(block.get("text") or "").strip():
            continue
        if block_type == "tool_use":
            normalized = dict(block)
            normalized.pop("partial_json", None)
            input_value = _input_from_fragments(normalized, fragments)
            if input_value is None:
                input_value = _input_from_tool_calls(normalized, tool_calls)
            if input_value is None:
                input_value = _parse_tool_input(json_by_index.get(normalized.get("index")))
            if input_value is not None and not normalized.get("input"):
                normalized["input"] = input_value
            elif normalized.get("input") == "":
                normalized["input"] = {}
            finalized.append(normalized)
            continue
        finalized.append(block)
    return finalized
