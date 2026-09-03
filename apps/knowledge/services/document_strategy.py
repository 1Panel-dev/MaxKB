"""Document import strategy normalization and deterministic fingerprints."""

import hashlib
import json
from copy import deepcopy
from typing import Dict, Iterable, List

from common.utils.split_model import SplitModel, get_split_model

DEFAULT_DOCUMENT_STRATEGY = {
    "split": {
        "mode": "smart",
        "patterns": None,
        "min_length": 0,
        "max_length": 4096,
        "child_length": 256,
        "auto_clean": False,
    },
    "visual": {
        "enabled": False,
        "strategy": "model",
        "model_id": None,
        "tool_id": None,
    },
    "index": {"title_as_question": False},
}


def _deep_merge(base: Dict, override: Dict) -> Dict:
    result = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def normalize_document_strategy(strategy: Dict | None) -> Dict:
    result = _deep_merge(DEFAULT_DOCUMENT_STRATEGY, strategy or {})
    split = result["split"]
    provided_split = (strategy or {}).get("split") or {}
    if "mode" not in provided_split and "patterns" in provided_split:
        split["mode"] = "advanced"
    if split.get("mode") not in {"smart", "advanced"}:
        split["mode"] = "smart"
    split["min_length"] = max(0, int(split.get("min_length") or 0))
    split["max_length"] = min(100000, max(50, int(split.get("max_length") or 4096)))
    if split["min_length"] > split["max_length"]:
        split["min_length"] = split["max_length"]
    split["child_length"] = min(2048, max(50, int(split.get("child_length") or 256)))
    patterns = split.get("patterns")
    if patterns is not None:
        split["patterns"] = [str(item) for item in patterns if item is not None]

    visual = result["visual"]
    visual["enabled"] = bool(visual.get("enabled", False))
    if visual.get("strategy") not in {"model", "tool"}:
        visual["strategy"] = "model"
    if visual["enabled"]:
        selected = visual.get("model_id") if visual["strategy"] == "model" else visual.get("tool_id")
        if not selected:
            raise ValueError("visual enhancement requires the selected model or tool")
    visual["model_id"] = str(visual["model_id"]) if visual.get("model_id") else None
    visual["tool_id"] = str(visual["tool_id"]) if visual.get("tool_id") else None
    result["index"]["title_as_question"] = bool(result["index"].get("title_as_question", False))
    return result


def parse_web_content(content: str, strategy: Dict | None) -> List[Dict]:
    """Parse Web content with the exact split strategy captured when the document was imported."""
    normalized = normalize_document_strategy(strategy)
    split = normalized["split"]
    patterns = split.get("patterns")
    parse_limit = 100000 if patterns == [] else split["max_length"]
    if patterns:
        split_model = SplitModel(patterns, with_filter=split["auto_clean"], limit=parse_limit)
    else:
        split_model = get_split_model("web.md", with_filter=split["auto_clean"], limit=parse_limit)
    return apply_length_strategy(split_model.parse(content), normalized)


def stable_hash(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def strategy_hashes(strategy: Dict | None) -> Dict[str, str]:
    normalized = normalize_document_strategy(strategy)
    return {
        "split_strategy_hash": stable_hash(normalized["split"]),
        "visual_strategy_hash": stable_hash(normalized["visual"]),
        "index_strategy_hash": stable_hash(normalized["index"]),
    }


def document_source_hash(paragraphs: Iterable[Dict]) -> str:
    return stable_hash([{"title": p.get("title") or "", "content": p.get("content") or ""} for p in paragraphs])


def apply_length_strategy(paragraphs: List[Dict], strategy: Dict | None) -> List[Dict]:
    """Apply max/min rules after structural parsing; a short tail merges into its predecessor."""
    split = normalize_document_strategy(strategy)["split"]
    if split.get("patterns") == []:
        parts = []
        for paragraph in paragraphs:
            title, content = paragraph.get("title") or "", paragraph.get("content") or ""
            value = "\n".join(item for item in [title, content] if item)
            if value.strip():
                parts.append(value)
        return [{"title": "", "content": "\n".join(parts)}] if parts else []
    maximum, minimum = split["max_length"], split["min_length"]
    result: List[Dict] = []
    for paragraph in paragraphs:
        content = paragraph.get("content") or ""
        if not content.strip():
            continue
        pieces = [content[i : i + maximum] for i in range(0, len(content), maximum)] or [content]
        for index, piece in enumerate(pieces):
            item = {**paragraph, "content": piece}
            if index:
                item["title"] = ""
            result.append(item)
    if minimum and len(result) > 1 and len(result[-1]["content"]) < minimum:
        tail = result.pop()
        separator = "\n" if result[-1]["content"] else ""
        result[-1]["content"] += separator + tail["content"]
    return result
