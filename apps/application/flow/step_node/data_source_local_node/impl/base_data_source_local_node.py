# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_data_source_local_node.py
    @date：2025/11/11 10:30
    @desc:
"""
from application.flow.i_step_node import NodeResult
from application.flow.step_node.data_source_local_node.i_data_source_local_node import IDataSourceLocalNode
from common import forms
from common.forms import BaseForm


class BaseDataSourceLocalNodeForm(BaseForm):
    api_key = forms.PasswordInputField('API Key', required=True)


class BaseDataSourceLocalNode(IDataSourceLocalNode):
    def save_context(self, details, workflow_manage):
        self.context['exception_message'] = details.get('err_message')

    @staticmethod
    def get_form_list(node):
        node_data = node.get('properties').get('node_data')
        return [{
            'field': 'file_list',
            'input_type': 'LocalFileUpload',
            'attrs': {
                'file_count_limit': node_data.get('file_count_limit') or 10,
                'file_size_limit': node_data.get('file_size_limit') or 100,
                'file_type_list': node_data.get('file_type_list'),
            },
            'label': '',
        }]

    def execute(self, file_type_list, file_size_limit, file_count_limit, **kwargs) -> NodeResult:
        return NodeResult({'file_list': self.workflow_manage.params.get('data_source', {}).get('file_list')},
                          self.workflow_manage.params.get('knowledge_base') or {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'file_list': self.context.get('file_list'),
            'knowledge_base': self.workflow_params.get('knowledge_base'),
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
