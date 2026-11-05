import time

from application.workflow.i_node import Signal
from application.workflow.status import Status
from knowledge.models.knowledge_action import State
from tools.models import ToolRecord


def save_workflow_tool_record(
    tool_record_id, tool_id, workspace_id, source_type, source_id, wf_manage, aggregation, parameters, start_time, error
):
    """Persist workflow tool executions from both workflow nodes and AI tool calls."""
    base_node = wf_manage.workflow.get_node("tool-base-node")
    input_field_list = base_node.properties.get("user_input_field_list", []) if base_node else []
    output_field_list = base_node.properties.get("user_output_field_list", []) if base_node else []
    input_data = {f.get("field"): parameters.get(f.get("field")) for f in input_field_list}
    output = wf_manage.context.get("output", {})
    details = wf_manage.get_details()
    if wf_manage.signal == Signal.CANCELLED:
        state = State.REVOKED
    elif error:
        state = State.FAILURE
    else:
        has_fail = any((d or {}).get("status") == Status.FAIL.value for d in (details or []))
        state = State.FAILURE if has_fail else State.SUCCESS
    ToolRecord(
        id=tool_record_id,
        tool_id=tool_id,
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        state=state,
        run_time=time.time() - start_time,
        meta={
            "input_field_list": input_field_list,
            "output_field_list": output_field_list,
            "input": input_data,
            "output": output,
            "details": details,
            "answer_text_list": aggregation.get_contents(),
        },
    ).save()
