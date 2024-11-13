# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_form_node.py
    @date：2024/11/4 14:52
    @desc:
"""
import json
import time
from typing import Dict

from langchain_core.prompts import PromptTemplate

from application.flow.i_step_node import NodeResult
from application.flow.step_node.form_node.i_form_node import IFormNode


def write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable is not None:
        for key in step_variable:
            node.context[key] = step_variable[key]
        if workflow.is_result(node, NodeResult(step_variable, global_variable)) and 'result' in step_variable:
            result = step_variable['result']
            yield result
            node.answer_text = result
    node.context['run_time'] = time.time() - node.context['start_time']


class BaseFormNode(IFormNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.context['form_content_format'] = details.get('form_content_format')
        self.context['form_field_list'] = details.get('form_field_list')
        self.context['run_time'] = details.get('run_time')
        self.context['start_time'] = details.get('start_time')
        self.answer_text = details.get('result')

    def execute(self, form_field_list, form_content_format, **kwargs) -> NodeResult:
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting)}</form_rander>'
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form)
        return NodeResult(
            {'result': value, 'form_field_list': form_field_list, 'form_content_format': form_content_format}, {},
            _write_context=write_context)

    def get_answer_text(self):
        form_content_format = self.context.get('form_content_format')
        form_field_list = self.context.get('form_field_list')
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        'form_data': self.context.get('form_data', {}),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting)}</form_rander>'
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form)
        return value

    def get_details(self, index: int, **kwargs):
        form_content_format = self.context.get('form_content_format')
        form_field_list = self.context.get('form_field_list')
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        'form_data': self.context.get('form_data', {}),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting)}</form_rander>'
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form)
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": value,
            "form_content_format": self.context.get('form_content_format'),
            "form_field_list": self.context.get('form_field_list'),
            'form_data': self.context.get('form_data'),
            'start_time': self.context.get('start_time'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
