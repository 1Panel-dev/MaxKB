# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： i_node.py
@date：2026/6/29  16:41
@desc:
"""

import time
from enum import Enum
from typing import Optional, Type, Callable

from rest_framework import serializers

from application.workflow.common import Node
from application.workflow.message.struct.content import Content
from application.workflow.status import Status
from common.utils.logger import maxkb_logger


class CancelledException(Exception):
    """工作流取消异常"""

    pass


class Signal(str, Enum):
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    FORM = "FORM"
    CANCELLED = "CANCELLED"


class INode:
    # 当前节点支持的工作流类型
    supported_workflow_type_list = []
    # 节点类型
    type = None
    # 序列化校验器
    serializer_class: Optional[Type[serializers.Serializer]] = None

    @staticmethod
    def is_valid(data):
        INode.serializer_class(data=data).is_valid(raise_exception=True)

    def __init__(self, node, workflow_manage, get_node_parameters: Callable[[Node], dict]):
        self.node = node
        self.status = Status.BEFORE_RUNNING
        self.workflow_manage = workflow_manage
        # 节点参数
        self.parameters = get_node_parameters(node)
        # 节点运行时产生的数据
        self.data = {}
        self._completed = False
        # ---- 锚点构造,全项目唯一的拼接点 ----

    def anchor(self, *parts):
        """
        通用锚点: anchor('right') → '{id}_right',
                anchor(branch_id, 'right') → '{id}_{branch_id}_right'
        """
        return "_".join([self.node.id, *map(str, parts)])

    def success_anchor(self):
        """
        成功锚点
        @return: 成功锚点
        """
        return self.anchor("right")

    def fail_anchor(self):
        """
        失败锚点
        @return: 失败锚点
        """
        return self.branch_anchor("exception")

    def branch_anchor(self, branch_id):
        """
        自定义锚点
        @param branch_id: 自定义分支id
        @return: 自定义锚点
        """
        return self.anchor(branch_id, "right")

    def execute(self):
        pass

    def run(self):
        """
        运行节点
        @return: 不响应数据
        """
        self.data["start_time"] = time.time()
        self.status = Status.RUNNING
        try:
            self._run()
        except CancelledException:
            self.complete(Status.CANCELLED)
        except Exception as e:
            self.complete(Status.FAIL, error=e)

    def _run(self):
        """
        执行节点
        @return:
        """
        self.execute()
        self.complete(Status.SUCCESS)

    def complete(self, status, anchors=None, error=None, signal: Optional[Signal] = None):
        """
        节点结束调用函数

        @param status: 状态
        @param anchors 锚点信息
        @param error:  错误信息
        @param signal: 信号
        @return:
        """
        if self._completed:
            return
        self._completed = True
        self.status = status
        if error:
            self.data["error"] = str(error)
        self.data["run_time"] = time.time() - self.data["start_time"]
        if signal:
            self.workflow_manage.signal = signal
            anchors = []
        if anchors is None:
            anchors = [
                self.success_anchor() if [Status.SUCCESS, Status.CANCELLED].__contains__(status) else self.fail_anchor()
            ]
        self._dispatch(anchors)
        self.workflow_manage.assertion_end(error)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        """
        获取节点运行详情
        @param index: 节点索引
        @param position: 位置信息，用于表单节点等断点续跑场景
        @param old_details: 旧的详情数据，用于表单节点等断点续跑场景
        @return: 节点详情字典
        """
        return {
            "node_id": self.node.id,
            "name": self.get_node_name(),
            "index": index,
            "run_time": self.data.get("run_time"),
            "type": self.type,
            "status": self.status.value if self.status else None,
            "error": self.data.get("error"),
        }

    def _dispatch(self, anchors):
        """
        根据锚点执行下一个节点
        @param anchors: 锚点列表
        @return:不返回
        """
        edge_node_list = self.workflow_manage.workflow.get_next_edge_nodes(self.node.id) or []
        known = {en.edge.sourceAnchorId for en in edge_node_list}
        unknown = set(anchors) - known
        if unknown and known:
            maxkb_logger.warning(f"node {self.node.id}: anchors {unknown} matched no edges, known={known}")
        self.workflow_manage.next_nodes([en.node for en in edge_node_list if en.edge.sourceAnchorId in anchors])

    def get_node_id(self):
        """
        获取节点id
        @return: 节点id
        """
        return self.node.id

    def get_node_name(self):
        """
        获取节点名称
        @return: 节点名称
        """
        return self.node.properties.get("stepName")

    def write_context(self, key, value, append=False):
        """
        将数据写入节点上下文
        @param key:   数据key
        @param value: 数据value
        @param append: 是否追加
        @return: None
        """
        self.workflow_manage.write_context(self.node.id, key, value, append)

    def get_context(self, key):
        """
        获取上下文数据 根据key
        @param key: key
        @return: 数据
        """
        return self.workflow_manage.get_context(self.node.id, key)

    def get_workflow_type(self):
        """
        获取工作流类型
        @return: 工作流类型
        """
        return self.workflow_manage.workflow_type

    def get_workflow_parameters(self):
        """
        获取工作流body
        @return: 工作流body数据
        """
        return self.workflow_manage.get_parameters()

    def get_parameters(self):
        """
        获取节点参数数据
        @return: 节点参数数据
        """
        return self.parameters

    def get_next_nodes(self, wf):
        """
        获取下n个基点
        @param wf: 工作流对象
        @return:  下n个节点
        """
        return wf.get_next_nodes(self.get_node_id())

    def write(self, message: Content):
        self.workflow_manage.write(message)

    def cancel(self):
        """
        取消运行
        @return:
        """
        self.status = Status.CANCELLED

    def _check_cancelled(self):
        """
        检查是否已取消，如果已取消则抛出 CancelledException
        @return:
        """
        if self.status == Status.CANCELLED or self.workflow_manage.signal == Signal.CANCELLED:
            raise CancelledException()
