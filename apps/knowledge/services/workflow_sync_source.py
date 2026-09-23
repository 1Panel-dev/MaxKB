"""Validate the saved input used to rerun a workflow knowledge data source."""


def validate_workflow_sync_source(work_flow: dict, workflow_input: dict) -> None:
    data_source = workflow_input.get("data_source") or {}
    node_id = data_source.get("node_id")
    if not node_id:
        raise ValueError("Run the workflow once before enabling scheduled synchronization")
    source_node = next((node for node in (work_flow or {}).get("nodes", []) if node.get("id") == node_id), None)
    if source_node is None or source_node.get("properties", {}).get("kind") != "data-source":
        raise ValueError("The saved workflow data source no longer exists")
    if source_node.get("type") == "data-source-local-node" or data_source.get("file_list"):
        raise ValueError("Local file data sources cannot be synchronized on a schedule")
    if source_node.get("type") == "data-source-web-node" and not str(data_source.get("source_url") or "").strip():
        raise ValueError("Web data source has no saved source URL")
