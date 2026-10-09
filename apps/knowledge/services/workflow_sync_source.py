"""Validate the saved input used to rerun a workflow knowledge data source."""

from knowledge.services.document_strategy import stable_hash


DOCUMENT_IDENTITY_FIELDS = ("source_key", "source_id", "token", "source_url", "url")
TOOL_SOURCE_FIELDS = (*DOCUMENT_IDENTITY_FIELDS, "source_type", "source_document_type")


def workflow_source_meta(work_flow: dict, workflow_input: dict) -> dict:
    """Identify one selected data source without persisting its credentials in documents."""
    data_source = workflow_input.get("data_source") or {}
    node_id = data_source.get("node_id")
    source_node = next((node for node in (work_flow or {}).get("nodes", []) if node.get("id") == node_id), None)
    if source_node is None:
        return {}
    node_type = source_node.get("type")
    node_data = source_node.get("properties", {}).get("node_data") or {}
    source_type = {
        "data-source-web-node": "web",
        "data-source-local-node": "local",
    }.get(node_type, "tool")
    source_input = {key: value for key, value in data_source.items() if key not in {"node_id", "file_list"}}
    if "file_list" in data_source:
        # Remote folder/document names can change without changing the selected source.
        source_input["file_list"] = sorted(
            [
                {key: item[key] for key in ("token", "type", "file_id") if key in item}
                for item in data_source.get("file_list") or []
            ],
            key=stable_hash,
        )
    meta = {
        "source_type": source_type,
        "source_node_id": str(node_id),
        "source_scope": stable_hash(
            {"node_id": node_id, "node_type": node_type, "node_data": node_data, "input": source_input}
        ),
    }
    if node_type == "tool-lib-node" and node_data.get("tool_lib_id"):
        meta["source_tool_id"] = str(node_data["tool_lib_id"])
    return meta


def tool_document_source_meta(item: dict | str, result: dict, node_id, tool_id, tool_name) -> dict:
    """Retain remote document identities, never download payloads or access credentials."""
    meta = {}
    if isinstance(item, str):
        meta["source_key"] = item
        item = {}
    for document in (item, result):
        for values in (document.get("meta") or {}, document):
            for field in TOOL_SOURCE_FIELDS:
                if isinstance(values.get(field), (str, int)) and str(values[field]).strip():
                    meta[field] = str(values[field]).strip()
            for field in ("document_token", "file_token"):
                if values.get(field):
                    meta.setdefault("token", str(values[field]))
        if document.get("type"):
            meta.setdefault("source_document_type", str(document["type"]))
    if item.get("id") and not any(meta.get(field) for field in DOCUMENT_IDENTITY_FIELDS):
        meta["source_id"] = str(item["id"])
    meta.setdefault("source_type", "tool")
    meta.update(source_node_id=str(node_id), source_tool_id=str(tool_id), source_tool_name=str(tool_name))
    return meta


def validate_workflow_sync_source(work_flow: dict, workflow_input: dict) -> None:
    data_source = workflow_input.get("data_source") or {}
    node_id = data_source.get("node_id")
    if not node_id:
        raise ValueError("Run the workflow once before enabling scheduled synchronization")
    source_node = next((node for node in (work_flow or {}).get("nodes", []) if node.get("id") == node_id), None)
    if source_node is None or source_node.get("properties", {}).get("kind") != "data-source":
        raise ValueError("The saved workflow data source no longer exists")
    file_list = data_source.get("file_list") or []
    remote_tool_files = source_node.get("type") == "tool-lib-node" and all(
        isinstance(item, dict) and item.get("token") and not item.get("file_id") for item in file_list
    )
    if source_node.get("type") == "data-source-local-node" or (file_list and not remote_tool_files):
        raise ValueError("Local file data sources cannot be synchronized on a schedule")
    if source_node.get("type") == "data-source-web-node" and not str(data_source.get("source_url") or "").strip():
        raise ValueError("Web data source has no saved source URL")
