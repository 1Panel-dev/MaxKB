# coding=utf-8
import json
from typing import List

from application.flow.i_step_node import NodeResult
from application.flow.step_node.variable_assign_node.i_variable_assign_node import IVariableAssignNode


class BaseVariableAssignNode(IVariableAssignNode):
    def save_context(self, details, workflow_manage):
        self.context['variable_list'] = details.get('variable_list')
        self.context['result_list'] = details.get('result_list')
        self.context['exception_message'] = details.get('err_message')

    def global_evaluation(self, variable, value):
        from application.flow.loop_workflow_manage import LoopWorkflowManage
        if isinstance(self.workflow_manage, LoopWorkflowManage):
            self.workflow_manage.parentWorkflowManage.context[variable['fields'][1]] = value
        else:
            self.workflow_manage.context[variable['fields'][1]] = value

    def loop_evaluation(self, variable, value):
        from application.flow.loop_workflow_manage import LoopWorkflowManage
        if isinstance(self.workflow_manage, LoopWorkflowManage):
            self.workflow_manage.get_loop_context()[variable['fields'][1]] = value

    def chat_evaluation(self, variable, value):
        from application.flow.loop_workflow_manage import LoopWorkflowManage
        if isinstance(self.workflow_manage, LoopWorkflowManage):
            self.workflow_manage.parentWorkflowManage.chat_context[variable['fields'][1]] = value
        else:
            self.workflow_manage.chat_context[variable['fields'][1]] = value

    def out_evaluation(self, variable, value):
        from application.flow.loop_workflow_manage import LoopWorkflowManage
        if isinstance(self.workflow_manage, LoopWorkflowManage):
            self.workflow_manage.parentWorkflowManage.out_context[variable['fields'][1]] = value
        else:
            self.workflow_manage.out_context[variable['fields'][1]] = value

    def handle(self, variable, evaluation):
        result = {
            'name': variable['name'],
            'input_value': self.get_reference_content(variable['fields']),
        }
        if variable['source'] == 'custom':
            if variable['type'] == 'json':
                if isinstance(variable['value'], dict) or isinstance(variable['value'], list):
                    val = variable['value']
                else:
                    val = json.loads(variable['value'])
                evaluation(variable, val)
                result['output_value'] = variable['value'] = val
            elif variable['type'] == 'string':
                # 变量解析 例如：{{global.xxx}}
                val = self.workflow_manage.generate_prompt(variable['value'])
                evaluation(variable, val)
                result['output_value'] = val
            else:
                val = variable['value']
                evaluation(variable, val)
                result['output_value'] = val
        elif variable['source'] == 'referencing':
            reference = self.get_reference_content(variable['reference'])
            evaluation(variable, reference)
            result['output_value'] = reference
        else:
            val = None
            evaluation(variable, val)
            result['output_value'] = val

        # 获取输入输出值的类型，用于显示在执行详情页面中
        result['input_type'] = type(result.get('input_value')).__name__ if result.get('input_value') is not None else 'null'
        result['output_type'] = type(result.get('output_value')).__name__ if result.get('output_value') is not None else 'null'

        return result

    def execute(self, variable_list, **kwargs) -> NodeResult:
        result_list = []
        contains_chat_variable = False
        for variable in variable_list:
            if not variable.get('fields'):
                continue

            field0 = variable['fields'][0]
            if 'global' == field0:
                result = self.handle(variable, self.global_evaluation)
                result_list.append(result)
            elif 'chat' == field0:
                result = self.handle(variable, self.chat_evaluation)
                result_list.append(result)
                contains_chat_variable = True
            elif 'loop' == field0:
                result = self.handle(variable, self.loop_evaluation)
                result_list.append(result)
            elif 'output' == field0:
                result = self.handle(variable, self.out_evaluation)
                result_list.append(result)

        if contains_chat_variable:
            from application.flow.loop_workflow_manage import LoopWorkflowManage
            if isinstance(self.workflow_manage, LoopWorkflowManage):
                self.workflow_manage.parentWorkflowManage.get_chat_info().set_chat_variable(
                    self.workflow_manage.parentWorkflowManage.chat_context)
            else:
                self.workflow_manage.get_chat_info().set_chat_variable(self.workflow_manage.chat_context)
        return NodeResult({'variable_list': variable_list, 'result_list': result_list}, {})

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:])

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'variable_list': self.context.get('variable_list'),
            'result_list': self.context.get('result_list'),
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
