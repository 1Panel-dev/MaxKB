# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： workflow_manage.py
    @date：2026/6/29 10:30
    @desc:
"""
from __future__ import annotations

import threading
from typing import List, Dict, Optional, Callable

from langchain_core.prompts import PromptTemplate

from application.flow.i_step_node import INode
from application.workflow.common import Workflow, WorkflowType, Node, get_node_parameters
from application.workflow.message.struct.content import Content
from application.workflow.nodes import get_node_class
from application.workflow.status import Status


class CallBack:
    def __init__(self, on_next: Callable[[WorkflowManage, Content], None],
                 on_complete: Callable[[WorkflowManage, Optional[Exception]], None]):
        self.on_next = on_next
        self.on_complete = on_complete


class WorkflowManage:
    # 工作流节点数据
    context: Dict[Dict[str, any]]
    # 运行的节点
    nodes: List[INode]
    # 是否结束
    done: bool

    def __init__(self,
                 workflow: Workflow,
                 parameters: Dict,
                 workflow_type: WorkflowType,
                 call_back: CallBack,
                 get_start_node: Callable[[Workflow, WorkflowManage], INode]):
        """

        @param workflow:      工作流对象
        @param workflow_type: 工作流类型
        @param parameters:    工作流使用到的其他数据
        """
        self._lock = threading.Lock()
        self.done = False
        self.call_back = call_back
        self.workflow = workflow
        self.workflow_type = workflow_type
        self.parameters = parameters
        self.context = {}
        self.nodes = []
        self.start_node = get_start_node(workflow, self)

    def run(self):
        """
        工作流执行
        @return: None
        """
        self._run_async(self.start_node)

    def _run(self, node):
        self.nodes.append(node)
        node.run()

    def next_nodes(self, nodes: Optional[List[Node]]):
        """
        继续执行下面的节点
        @param nodes: 执行下面要执行的节点
        @return:
        """
        if nodes is None or len(nodes) == 0:
            return
        with self._lock:
            instances = [get_node_class(n.type, self.workflow_type)(n, self, get_node_parameters)
                         for n in nodes]
            self.nodes.extend(instances)
        for inst in instances:
            self._run_async(inst)

    def assertion_end(self):
        """
        如果节点执行结束没有下一个节点  就结束工作流
        @return:
        """
        with self._lock:
            if self.done:
                return
            if not self.is_end():
                return
            self.done = True
        self.end()

    def is_end(self):
        """
        工作流是否执行结束
        @return: 是否执行结束
        """
        unfinished = {Status.BEFORE_RUNNING, Status.RUNNING}
        return not any(node.status in unfinished for node in self.nodes)

    def write_context(self, node_id, key, value, append=False):
        """
        写入上下文
        @param node_id: 节点id
        @param key:     数据key
        @param value:   数据value
        @param append:  是否追加
        @return: None
        """
        node_context = self.context.setdefault(node_id, {})
        if append and key in node_context:
            node_context[key] += value
        else:
            node_context[key] = value

    def get_context(self, node_id, key):
        """
        获取节点上下文的指定key的内容
        @param node_id:  节点id
        @param key:      key
        @return: 数据
        """
        return self.context.setdefault(node_id).get(key)

    def _run_async(self, node):
        t = threading.Thread(target=lambda: self._run(node))
        t.start()
        return t

    def invoke(self):
        """
        非流式响应
        @return: 没个节点的 块数据
        """
        self.run()

    def write(self, message: Content):
        """
        写入数据
        @param message: 节点输出内容
        @return: None
        """
        self.call_back.on_next(self, message)

    def end(self):
        """
        工作流输出结束的时候调用
        @return: None
        """
        if self.done:
            return
        self.call_back.on_complete(self, None)
        self.done = True

    def get_parameters(self):
        """
        获取工作流的参数信息
        @return: 工作流参数信息
        """
        return self.parameters

    def generate_prompt(self, prompt):
        """
        处理提示词
        @param prompt: 提示词
        @return: 处理后的提示词
        """
        prompt = self.workflow.reset_prompt(prompt)
        prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
        return prompt_template.format(context=self.context)

    def get_reference_field(self, node_id, fields):
        """
        获取引用字段
        @param node_id: 节点id
        @param fields:   字段
        @return: 引用数据
        """
        node_context = self.context.get(node_id)
        if node_context is None:
            return None
        obj = node_context
        for field in fields:
            if isinstance(obj, dict):
                obj = obj.get(field)
            else:
                return None
        return obj
