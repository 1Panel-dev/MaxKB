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

    def convert(self, val, target_type):
        if not target_type or val is None:
            return val

        if target_type == 'json_object':
            if isinstance(val, dict) or isinstance(val, list):
                return val
            return json.loads(val)
        elif target_type == 'json_string':
            if isinstance(val, str):
                return val
            return json.dumps(val, ensure_ascii=False)
        elif target_type == 'string':
            if isinstance(val, str):
                return val
            return str(val)
        elif target_type == 'int':
            if isinstance(val, int):
                return val
            return int(val)
        elif target_type == 'float':
            if isinstance(val, float):
                return val
            return float(val)
        elif target_type == 'boolean':
            if isinstance(val, bool):
                return val
            return bool(val)
        else:
            return val

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
                val = self.convert(val, variable['target_type'])
                evaluation(variable, val)
                result['output_value'] = variable['value'] = val
            elif variable['type'] == 'string':
                # 变量解析 例如：{{global.xxx}}
                val = self.workflow_manage.generate_prompt(variable['value'])
                val = self.convert(val, variable['target_type'])
                evaluation(variable, val)
                result['output_value'] = val
            else:
                val = variable['value']
                val = self.convert(val, variable['target_type'])
                evaluation(variable, val)
                result['output_value'] = val
        else:
            reference = self.get_reference_content(variable['reference'])
            reference = self.convert(reference, variable['target_type'])
            evaluation(variable, reference)
            result['output_value'] = reference
        return result

    def execute(self, variable_list, **kwargs) -> NodeResult:
        #
        result_list = []
        contains_chat_variable = False
        for variable in variable_list:
            if 'fields' not in variable:
                continue

            if 'global' == variable['fields'][0]:
                result = self.handle(variable, self.global_evaluation)
                result_list.append(result)
            elif 'chat' == variable['fields'][0]:
                result = self.handle(variable, self.chat_evaluation)
                result_list.append(result)
                contains_chat_variable = True
            elif 'loop' == variable['fields'][0]:
                result = self.handle(variable, self.loop_evaluation)
                result_list.append(result)
            elif 'output' == variable['fields'][0]:
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
