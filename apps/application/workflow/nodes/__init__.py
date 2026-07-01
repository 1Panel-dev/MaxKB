# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： __init__.py.py
    @date：2026/6/29 16:15
    @desc:
"""
import pkgutil
import importlib
import inspect
from pathlib import Path

from application.workflow.i_node import INode

node_list: list[type[INode]] = []
_seen: set[type] = set()

for _, module_name, _ in pkgutil.iter_modules([str(Path(__file__).parent)]):
    module = importlib.import_module(f".{module_name}", __package__)
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if (
                issubclass(obj, INode)
                and obj is not INode
                and obj.__module__.startswith(__package__)
                and obj not in _seen
        ):
            _seen.add(obj)
            node_list.append(obj)

if not node_list:
    raise RuntimeError(f"未发现任何节点,检查各子包 __init__.py 是否导出了 INode 子类: {Path(__file__).parent}")

node_map = {n.type: {workflow_type: n for workflow_type in n.supported_workflow_type_list} for n in node_list}


def get_node_class(_type, workflow_type):
    """
    根据节点类型 获取此类型的处理器
    @param _type:         节点类型
    @param workflow_type: 工作流类型
    @return:      节点处理器
    """
    node_class = node_map.get(_type, {}).get(workflow_type)
    if node_class is None:
        raise ValueError(f"节点不存在: type={_type}, workflow_type={workflow_type}")
    return node_class


def get_start_node(workflow, workflow_manage, workflow_type):
    """
    获取开始节点实例
    @param workflow:       工作流对象
    @param workflow_manage 工作流管理器
    @param workflow_type:  工作流类型
    @return: 开始节点实例
    """
    start_node = workflow.get_node('start-node')
    if start_node is None:
        raise ValueError("开始节点不存在")
    node_class = get_node_class(start_node.type, workflow_type)

    def get_node_parameters(node):
        return node.properties.get('node_data', {})

    return node_class(start_node, workflow_manage, get_node_parameters)
