# coding=utf-8
"""
@project: MaxKB
@file： visibility_compat.py
@desc: 把 v2 工作流中引用本表单的显隐条件转换为 v3 格式。

v2 开始节点以 ``global`` 指代自身表单，表单节点以节点 ID（或占位 ``self-form``）指代自身表单，
两者都不保存 ``self``；v3 只按 ``self: true`` 从本表单取左值，否则字段始终判定为隐藏。
迁移 ``application.0016_v3_upgrade`` 直接依赖本模块：不要改名、删除或改变转换行为；
确需调整时，先把当前实现复制进该迁移，再修改这里。
"""

BASE_NODE_ID = "base-node"
_BASE_NODE_SELF_SCOPES = {"global", BASE_NODE_ID}
_FORM_NODE_PLACEHOLDER = "self-form"


def _normalize_field_list(field_list, self_scopes, node_id) -> bool:
    changed = False
    for field in field_list if isinstance(field_list, list) else []:
        rules = field.get("visibility_rules") if isinstance(field, dict) else None
        conditions = rules.get("conditions") if isinstance(rules, dict) else None
        for condition in conditions if isinstance(conditions, list) else []:
            cond_field = condition.get("field") if isinstance(condition, dict) else None
            if not isinstance(cond_field, list) or len(cond_field) < 2 or cond_field[0] not in self_scopes:
                continue
            if cond_field[0] != node_id:
                cond_field[0] = node_id
                changed = True
            if condition.get("self") is not True:
                condition["self"] = True
                changed = True
    return changed


def _normalize_node(node) -> bool:
    if not isinstance(node, dict):
        return False
    properties = node.get("properties") or {}
    node_data = properties.get("node_data") or {}
    changed = False
    if node.get("id") == BASE_NODE_ID:
        changed |= _normalize_field_list(properties.get("user_input_field_list"), _BASE_NODE_SELF_SCOPES, BASE_NODE_ID)
    elif node.get("type") == "form-node" and node.get("id"):
        node_id = node["id"]
        changed |= _normalize_field_list(node_data.get("form_field_list"), {node_id, _FORM_NODE_PLACEHOLDER}, node_id)
    elif node.get("type") == "loop-node":
        for child in (node_data.get("loop_body") or {}).get("nodes") or []:
            changed |= _normalize_node(child)
    return changed


def normalize_workflow_visibility(work_flow) -> bool:
    """原地转换工作流中的显隐条件，返回是否有改动。"""
    if not isinstance(work_flow, dict):
        return False
    changed = False
    for node in work_flow.get("nodes") or []:
        changed |= _normalize_node(node)
    return changed
