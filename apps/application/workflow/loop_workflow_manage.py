# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： loop_workflow_manage.py
@date：2026/7/2 10:00
@desc:
"""

from typing import Dict, Callable, List

from application.workflow.common import Workflow, WorkflowType
from application.workflow.i_node import INode
from application.workflow.workflow_manage import WorkflowManage, CallBack


def get_loop_variable_fields(loop_start_properties) -> List[str]:
    """
    从循环开始节点的属性里取出声明的循环变量名
    @param loop_start_properties: loop-start-node 的 properties
    @return: 循环变量名列表
    """
    field_list = (loop_start_properties or {}).get("loop_input_field_list") or []
    fields = [item.get("field") or item.get("variable") for item in field_list if isinstance(item, dict)]
    return [field for field in fields if field]


class LoopWorkFlowManage(WorkflowManage):
    """
    循环体工作流。

    循环变量不存放在循环体自己的上下文里,而是存放在父工作流中“循环节点”的上下文下
    (parent.context[loop_node_id][变量名]):各轮共享、循环结束后下游可直接用 [循环节点ID, 变量名] 引用。
    循环体内的 ["loop", 变量名] 只是它的别名。
    """

    def __init__(
        self,
        workflow: Workflow,
        parameters: Dict,
        workflow_type: WorkflowType,
        call_back: CallBack,
        get_start_node: Callable[[Workflow, WorkflowManage], INode],
        parent_workflow_manage: WorkflowManage,
        loop_node_id: str = None,
    ):
        self.parent_workflow_manage = parent_workflow_manage
        self.loop_node_id = loop_node_id
        loop_start_node = workflow.get_node("loop-start-node")
        self.loop_variable_fields = get_loop_variable_fields(loop_start_node.properties if loop_start_node else None)
        super().__init__(workflow, parameters, workflow_type, call_back, get_start_node)

    def get_parameters(self):
        return self.parameters

    def get_parent_context(self, node_id, key):
        return self.parent_workflow_manage.get_context(node_id, key)

    def _loop_variable_owner(self, field):
        """
        找到循环变量所属的循环:优先是声明了该变量的最近一层循环,都没有声明则归当前循环
        @param field: 循环变量名
        @return: 所属循环的 LoopWorkFlowManage
        """
        manage = self
        while field not in manage.loop_variable_fields and isinstance(
            manage.parent_workflow_manage, LoopWorkFlowManage
        ):
            manage = manage.parent_workflow_manage
        return manage if field in manage.loop_variable_fields else self

    def write_context(self, node_id, key, value, append=False):
        """
        写入上下文:节点属于当前循环体就写自己,否则交给父工作流(父工作流是循环则继续向上)。
        循环变量(node_id 为 loop)写到所属循环的循环节点上下文里。
        """
        if node_id == "loop" and self.loop_node_id:
            owner = self._loop_variable_owner(key)
            owner.parent_workflow_manage.write_context(owner.loop_node_id, key, value, append)
            return
        if self.workflow.get_node(node_id) is not None:
            super().write_context(node_id, key, value, append)
            return
        self.parent_workflow_manage.write_context(node_id, key, value, append)

    def reset_prompt(self, prompt):
        input_template = self.workflow.reset_prompt(prompt)
        if self.loop_node_id:
            # 长的变量名先替换,避免 loop.ab 被 loop.a 截断
            for field in sorted(self.loop_variable_fields, key=len, reverse=True):
                system_variable = f"(context.get('{self.loop_node_id}') or {{}}).get('{field}','')"
                input_template = input_template.replace(f"循环变量.{field}", system_variable)
                input_template = input_template.replace(f"loop.{field}", system_variable)
        return self.parent_workflow_manage.reset_prompt(input_template)

    def get_merged_context(self):
        """
        祖先工作流上下文 + 自己的上下文,同名时以自己为准
        """
        return {**self.parent_workflow_manage.get_merged_context(), **self.context}

    def get_reference_field(self, node_id, fields):
        """
        获取引用字段，先从当前工作流获取，获取不到再从父工作流获取
        @param node_id: 节点id
        @param fields:   字段
        @return: 引用数据
        """
        if node_id == "loop" and self.loop_node_id and fields:
            owner = self._loop_variable_owner(fields[0])
            return owner.parent_workflow_manage.get_reference_field(owner.loop_node_id, fields)

        # 先从当前工作流获取
        result = super().get_reference_field(node_id, fields)
        if result is not None:
            return result

        # 从父工作流获取
        return self.parent_workflow_manage.get_reference_field(node_id, fields)

    @classmethod
    def from_context(
        cls,
        get_context,
        workflow,
        parameters,
        workflow_type,
        call_back,
        get_start_node,
        parent_workflow_manage=None,
        loop_node_id=None,
    ):
        try:
            context = get_context()

            instance = cls(
                workflow=workflow,
                parameters=parameters,
                workflow_type=workflow_type,
                call_back=call_back,
                get_start_node=get_start_node,
                parent_workflow_manage=parent_workflow_manage,
                loop_node_id=loop_node_id,
            )
            if context:
                instance.context = context

            return instance
        except Exception:
            import traceback

            traceback.print_exc()
            return None
