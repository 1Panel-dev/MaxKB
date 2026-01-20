# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： base_data_source_web_node.py
    @date：2025/11/12 13:47
    @desc:
"""
import traceback

from django.utils.translation import gettext_lazy as _

from application.flow.i_step_node import NodeResult
from application.flow.step_node.data_source_web_node.i_data_source_web_node import IDataSourceWebNode
from common import forms
from common.forms import BaseForm
from common.utils.fork import ForkManage, Fork, ChildLink
from common.utils.logger import maxkb_logger


class BaseDataSourceWebNodeForm(BaseForm):
    source_url = forms.TextInputField(_('Web source url'), required=True, attrs={
        'placeholder': _('Please enter the Web root address')})
    selector = forms.TextInputField(_('Web knowledge selector'), required=False, attrs={
        'placeholder': _('The default is body, you can enter .classname/#idname/tagname')})


class InterruptedTaskException(Exception):
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


def get_collect_handler(workflow_manage):
    results = []

    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            try:
                document_name = child_link.tag.text if child_link.tag is not None and len(
                    child_link.tag.text.strip()) > 0 else child_link.url
                results.append({
                    "name": document_name.strip(),
                    "content": response.content,
                })

            except Exception as e:
                maxkb_logger.error(f'{str(e)}:{traceback.format_exc()}')
        if workflow_manage.is_the_task_interrupted():
            raise InterruptedTaskException('Task interrupted')

    return handler, results


class BaseDataSourceWebNode(IDataSourceWebNode):
    def save_context(self, details, workflow_manage):
        self.context['exception_message'] = details.get('err_message')

    @staticmethod
    def get_form_list(node):
        return BaseDataSourceWebNodeForm().to_form_list()

    def execute(self, **kwargs) -> NodeResult:
        BaseDataSourceWebNodeForm().valid_form(self.workflow_params.get("data_source"))

        data_source = self.workflow_params.get("data_source")

        node_id = data_source.get("node_id")
        source_url = data_source.get("source_url")
        selector = data_source.get("selector") or "body"

        collect_handler, document_list = get_collect_handler(self.workflow_manage)

        try:
            ForkManage(source_url, selector.split(" ") if selector is not None else []).fork(3, set(), collect_handler)

            return NodeResult({'document_list': document_list, 'source_url': source_url, 'selector': selector},
                              self.workflow_manage.params.get('knowledge_base') or {})

        except Exception as e:
            if isinstance(e, InterruptedTaskException):
                return NodeResult({'document_list': document_list, 'source_url': source_url, 'selector': selector},
                                  self.workflow_manage.params.get('knowledge_base') or {})
            maxkb_logger.error(_('data source web node:{node_id} error{error}{traceback}').format(
                knowledge_id=node_id, error=str(e), traceback=traceback.format_exc()))

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'input_params': {"source_url": self.context.get("source_url"), "selector": self.context.get('selector')},
            'output_params': self.context.get('document_list'),
            'knowledge_base': self.workflow_params.get('knowledge_base'),
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
