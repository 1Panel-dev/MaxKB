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
from typing import Dict, List

from langchain_core.prompts import PromptTemplate

from application.flow.common import Answer
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
        form_data = details.get('form_data', None)
        self.context['result'] = details.get('result')
        self.context['form_content_format'] = details.get('form_content_format')
        self.context['form_field_list'] = details.get('form_field_list')
        self.context['run_time'] = details.get('run_time')
        self.context['start_time'] = details.get('start_time')
        self.context['form_data'] = form_data
        self.context['is_submit'] = details.get('is_submit')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('result')
        if form_data is not None:
            for key in form_data:
                self.context[key] = form_data[key]

    def execute(self, form_field_list, form_content_format, form_data, **kwargs) -> NodeResult:
        if form_data is not None:
            self.context['is_submit'] = True
            self.context['form_data'] = form_data
            for key in form_data:
                self.context[key] = form_data.get(key)
        else:
            self.context['is_submit'] = False
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting, ensure_ascii=False)}</form_rander>'
        context = self.workflow_manage.get_workflow_content()
        form_content_format = self.workflow_manage.reset_prompt(form_content_format)
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form, context=context)
        return NodeResult(
            {'result': value, 'form_field_list': form_field_list, 'form_content_format': form_content_format}, {},
            _write_context=write_context)

    def get_answer_list(self) -> List[Answer] | None:
        form_content_format = self.context.get('form_content_format')
        form_field_list = self.context.get('form_field_list')
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        'form_data': self.context.get('form_data', {}),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting, ensure_ascii=False)}</form_rander>'
        context = self.workflow_manage.get_workflow_content()
        form_content_format = self.workflow_manage.reset_prompt(form_content_format)
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form, context=context)
        return [Answer(value, self.view_type, self.runtime_node_id, self.workflow_params['chat_record_id'], None,
                       self.runtime_node_id, '')]

    def get_details(self, index: int, **kwargs):
        form_content_format = self.context.get('form_content_format')
        form_field_list = self.context.get('form_field_list')
        form_setting = {"form_field_list": form_field_list, "runtime_node_id": self.runtime_node_id,
                        "chat_record_id": self.flow_params_serializer.data.get("chat_record_id"),
                        'form_data': self.context.get('form_data', {}),
                        "is_submit": self.context.get("is_submit", False)}
        form = f'<form_rander>{json.dumps(form_setting, ensure_ascii=False)}</form_rander>'
        context = self.workflow_manage.get_workflow_content()
        form_content_format = self.workflow_manage.reset_prompt(form_content_format)
        prompt_template = PromptTemplate.from_template(form_content_format, template_format='jinja2')
        value = prompt_template.format(form=form, context=context)
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": value,
            "form_content_format": self.context.get('form_content_format'),
            "form_field_list": self.context.get('form_field_list'),
            'form_data': self.context.get('form_data'),
            'start_time': self.context.get('start_time'),
            'is_submit': self.context.get('is_submit'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
