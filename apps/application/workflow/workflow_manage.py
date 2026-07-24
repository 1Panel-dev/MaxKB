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

from application.workflow.common import Workflow, WorkflowType, Node, get_node_parameters
from application.workflow.i_node import INode, Signal
from application.workflow.message.struct.content import Content

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
        self.node_dict = {}
        self.signal = None
        self.start_node = get_start_node(workflow, self)

    def run(self):
        """
        工作流执行
        @return: None
        """
        self.nodes.append(self.start_node)
        self.node_dict = {node.node.id: node for node in self.nodes}
        self._run_async(self.start_node)

    def _run(self, node):
        node.run()

    def next_nodes(self, nodes: Optional[List[Node]]):
        """
        继续执行下面的节点
        @param nodes: 执行下面要执行的节点
        @return:
        """
        if [Signal.FORM, Signal.CANCELLED].__contains__(self.signal):
            return
        if nodes is None or len(nodes) == 0:
            return
        # 需要校验是否可执行
        for n in nodes:
            condition = n.properties.get("condition")
            if condition == 'AND':
                up_nodes = self.workflow.get_up_nodes(n.id)
                # 如果是AND就是前面所有节点都执行结束
                unfinished = {Status.BEFORE_RUNNING, Status.RUNNING}
                end = all(
                    [self.node_dict.get(node.id) and self.node_dict.get(node.id).status not in unfinished for node in
                     up_nodes])
                if not end:
                    return

        with self._lock:
            from application.workflow.nodes import get_node_class
            instances = [get_node_class(n.type, self.workflow_type)(n, self, get_node_parameters)
                         for n in nodes]
            self.nodes.extend(instances)
            for node in instances:
                self.node_dict[node.node.id] = node
        for inst in instances:
            self._run_async(inst)

    def assertion_end(self, error=None):
        with self._lock:
            if self.done:
                return
            if not self.is_end():
                return
            self.done = True  # 锁内抢占,保证只有一个线程能往下走
        self.end(error)  # 回调放到锁外,避免回调里再触碰本 manage 造成重入/死锁

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
        node_context = self.context.get(node_id)
        if node_context is None:
            return None
        return node_context.get(key)

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

    def end(self, error=None):
        """
        工作流输出结束的时候调用
        @return: None
        """
        self.call_back.on_complete(self, error)

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

    @classmethod
    def from_context(cls, chat_record_id, workflow, parameters, workflow_type,
                     call_back, get_start_node):
        """从历史 context 恢复 WorkflowManage"""
        from application.models import ChatRecord
        from django.core.cache import cache
        from common.constants.cache_version import Cache_Version

        try:
            context_data = None

            # 先从 Redis 查（调试模式）
            cache_key = Cache_Version.DEBUG_WORKFLOW_CONTEXT.get_key(chat_record_id=str(chat_record_id))
            context_data = cache.get(cache_key)

            # Redis 没有，从数据库查
            if not context_data:
                chat_record = ChatRecord.objects.filter(id=chat_record_id).first()
                if not chat_record or not chat_record.workflow_context:
                    return None
                context_data = chat_record.workflow_context

            # 创建 WorkflowManage 实例
            instance = cls(
                workflow=workflow,
                parameters=parameters,
                workflow_type=workflow_type,
                call_back=call_back,
                get_start_node=get_start_node
            )

            # 恢复全局 context
            instance.context = context_data

            return instance
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    def cancel(self):
        self.signal = Signal.CANCELLED
        for node in self.nodes:
            node.cancel()
