# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    resource.py
@desc:    工作流资源映射工具集。

这些函数只解析 work_flow 的 JSON 结构（nodes/properties/node_data），与具体执行引擎无关,
从旧引擎 application/flow/tools.py 迁出,作为新引擎下资源映射/工具依赖提取的统一入口。
"""

from functools import reduce

from django.db.models import QuerySet

from tools.models import Tool, ToolScope, ToolType, ToolWorkflow

# 节点类型 -> 其引用的目标资源 id 提取函数(按资源类型分组),供资源映射登记使用
target_source_node_mapping = {
    "TOOL": {
        "tool-lib-node": lambda n: [n.get("properties").get("node_data").get("tool_lib_id")],
        "ai-chat-node": lambda n: [
            *(n.get("properties").get("node_data").get("mcp_tool_ids") or []),
            *(n.get("properties").get("node_data").get("tool_ids") or []),
            *(n.get("properties").get("node_data").get("skill_tool_ids") or []),
        ],
        "mcp-node": lambda n: [n.get("properties").get("node_data").get("mcp_tool_id")],
        "tool-workflow-lib-node": lambda n: [n.get("properties").get("node_data").get("tool_lib_id")],
    },
    "MODEL": {
        "ai-chat-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "question-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "speech-to-text-node": lambda n: [n.get("properties").get("node_data").get("stt_model_id")],
        "text-to-speech-node": lambda n: [n.get("properties").get("node_data").get("tts_model_id")],
        "image-to-video-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "image-generate-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "intent-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "image-understand-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "parameter-extraction-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "video-understand-node": lambda n: [n.get("properties").get("node_data").get("model_id")],
        "reranker-node": lambda n: [n.get("properties").get("node_data").get("reranker_model_id")],
    },
    "KNOWLEDGE": {
        "search-knowledge-node": lambda n: n.get("properties").get("node_data").get("knowledge_id_list"),
        "search-document-node": lambda n: n.get("properties").get("node_data").get("knowledge_id_list"),
    },
    "APPLICATION": {
        "application-node": lambda n: [n.get("properties").get("node_data").get("application_id")],
        "ai-chat-node": lambda n: [*(n.get("properties").get("node_data").get("application_ids") or [])],
    },
}


def get_node_handle_callback(source_type, source_id):
    def node_handle_callback(node):
        from system_manage.models.resource_mapping import ResourceMapping

        response = []
        for key, value in target_source_node_mapping.items():
            if node.get("type") in value:
                call = value.get(node.get("type"))
                target_source_id_list = call(node)
                for target_source_id in target_source_id_list:
                    if target_source_id:
                        response.append(
                            ResourceMapping(
                                source_type=source_type,
                                target_type=key,
                                source_id=source_id,
                                target_id=target_source_id,
                            )
                        )
        return response

    return node_handle_callback


def get_workflow_resource(workflow, node_handle):
    response = []
    if "nodes" in workflow:
        for node in workflow.get("nodes"):
            rs = node_handle(node)
            if rs:
                for r in rs:
                    response.append(r)
            if node.get("type") == "loop-node":
                r = get_workflow_resource(node.get("properties", {}).get("node_data", {}).get("loop_body"), node_handle)
                for rn in r:
                    response.append(rn)
        return list({(str(item.target_type) + str(item.target_id)): item for item in response}.values())
    return []


application_instance_field_call_dict = {
    "TOOL": [
        lambda instance: instance.mcp_tool_ids or [],
        lambda instance: instance.skill_tool_ids or [],
        lambda instance: instance.tool_ids or [],
    ],
    "APPLICATION": [
        lambda instance: instance.application_ids or [],
    ],
    "MODEL": [
        lambda instance: [instance.model_id] if instance.model_id else [],
        lambda instance: [instance.long_term_model_id] if instance.long_term_model_id else [],
        lambda instance: [instance.tts_model_id] if instance.tts_model_id else [],
        lambda instance: [instance.stt_model_id] if instance.stt_model_id else [],
    ],
}
knowledge_instance_field_call_dict = {
    "MODEL": [lambda instance: [instance.embedding_model_id] if instance.embedding_model_id else []],
}


def get_instance_resource(instance, source_type, source_id, instance_field_call_dict):
    response = []
    from system_manage.models.resource_mapping import ResourceMapping

    for target_type, call_list in instance_field_call_dict.items():
        target_id_list = reduce(lambda x, y: [*x, *y], [call(instance) for call in call_list], [])
        if target_id_list:
            for target_id in target_id_list:
                response.append(
                    ResourceMapping(
                        source_type=source_type, target_type=target_type, source_id=source_id, target_id=target_id
                    )
                )
    return response


def save_workflow_mapping(workflow, source_type, source_id, other_resource_mapping=None):
    if not other_resource_mapping:
        other_resource_mapping = []
    from system_manage.models.resource_mapping import ResourceMapping

    QuerySet(ResourceMapping).filter(source_type=source_type, source_id=source_id).delete()
    resource_mapping_list = get_workflow_resource(workflow, get_node_handle_callback(source_type, source_id))
    resource_mapping_list += other_resource_mapping
    if resource_mapping_list:
        QuerySet(ResourceMapping).bulk_create(
            {(str(item.target_type) + str(item.target_id)): item for item in resource_mapping_list}.values()
        )


def get_tool_id_list(workflow, with_deep=False):
    _result = []
    for node in workflow.get("nodes", []):
        if node.get("type") == "tool-lib-node":
            tool_id = node.get("properties", {}).get("node_data", {}).get("tool_lib_id")
            if tool_id:
                _result.append(tool_id)
        elif node.get("type") == "loop-node":
            r = get_tool_id_list(node.get("properties", {}).get("node_data", {}).get("loop_body", {}))
            for item in r:
                _result.append(item)
        elif node.get("type") == "tool-workflow-lib-node":
            tool_id = node.get("properties", {}).get("node_data", {}).get("tool_lib_id")
            if tool_id:
                _result.append(tool_id)
        elif node.get("type") == "ai-chat-node":
            node_data = node.get("properties", {}).get("node_data", {})
            mcp_tool_ids = node_data.get("mcp_tool_ids") or []
            skill_tool_ids = node_data.get("skill_tool_ids") or []
            tool_ids = node_data.get("tool_ids") or []
            for _id in mcp_tool_ids + tool_ids + skill_tool_ids:
                _result.append(_id)
        elif node.get("type") == "mcp-node":
            mcp_tool_id = node.get("properties", {}).get("node_data", {}).get("mcp_tool_id")
            if mcp_tool_id:
                _result.append(mcp_tool_id)
    if with_deep:
        workflow_list = QuerySet(Tool).filter(id__in=_result, tool_type=ToolType.WORKFLOW)
        tool_work_flow_list = QuerySet(ToolWorkflow).filter(tool_id__in=[wl.id for wl in workflow_list])
        for tool_work_flow in tool_work_flow_list:
            child_tool_id_list = get_child_tool_id_list(tool_work_flow.work_flow, [])
            for c in child_tool_id_list:
                _result.append(c)
    return _result


def get_child_tool_id_list(work_flow, response):
    tool_id_list = get_tool_id_list(work_flow, False)
    tool_id_list = [tool_id for tool_id in tool_id_list if len([r for r in response if r == tool_id]) == 0]
    tool_list = []
    if len(tool_id_list) > 0:
        tool_list = QuerySet(Tool).filter(id__in=tool_id_list).exclude(scope=ToolScope.SHARED)
        work_flow_tools = [tool for tool in tool_list if tool.tool_type == ToolType.WORKFLOW]
        if len(work_flow_tools) > 0:
            work_flow_tool_dict = {
                tw.tool_id: tw for tw in QuerySet(ToolWorkflow).filter(tool_id__in=[t.id for t in work_flow_tools])
            }
            for tool in tool_list:
                response.append(str(tool.id))
                if tool.tool_type == ToolType.WORKFLOW:
                    get_child_tool_id_list(work_flow_tool_dict.get(tool.id).work_flow, response)
        else:
            for tool in tool_list:
                response.append(str(tool.id))
    return response
