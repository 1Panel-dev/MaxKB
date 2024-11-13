# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_step_node.py
    @date：2024/6/3 14:57
    @desc:
"""
import time
import uuid
from abc import abstractmethod
from typing import Type, Dict, List

from django.core import cache
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail

from application.models import ChatRecord
from application.models.api_key_model import ApplicationPublicAccessClient
from common.constants.authentication_type import AuthenticationType
from common.field.common import InstanceField
from common.util.field_message import ErrMessage

chat_cache = cache.caches['chat_cache']


def write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable is not None:
        for key in step_variable:
            node.context[key] = step_variable[key]
        if workflow.is_result(node, NodeResult(step_variable, global_variable)) and 'answer' in step_variable:
            answer = step_variable['answer']
            yield answer
            node.answer_text = answer
    if global_variable is not None:
        for key in global_variable:
            workflow.context[key] = global_variable[key]
    node.context['run_time'] = time.time() - node.context['start_time']


class WorkFlowPostHandler:
    def __init__(self, chat_info, client_id, client_type):
        self.chat_info = chat_info
        self.client_id = client_id
        self.client_type = client_type

    def handler(self, chat_id,
                chat_record_id,
                answer,
                workflow):
        question = workflow.params['question']
        details = workflow.get_runtime_details()
        message_tokens = sum([row.get('message_tokens') for row in details.values() if
                              'message_tokens' in row and row.get('message_tokens') is not None])
        answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                             'answer_tokens' in row and row.get('answer_tokens') is not None])
        answer_text_list = workflow.get_answer_text_list()
        answer_text = '\n\n'.join(answer_text_list)
        if workflow.chat_record is not None:
            chat_record = workflow.chat_record
            chat_record.answer_text = answer_text
            chat_record.details = details
            chat_record.message_tokens = message_tokens
            chat_record.answer_tokens = answer_tokens
            chat_record.answer_text_list = answer_text_list
            chat_record.run_time = time.time() - workflow.context['start_time']
        else:
            chat_record = ChatRecord(id=chat_record_id,
                                     chat_id=chat_id,
                                     problem_text=question,
                                     answer_text=answer_text,
                                     details=details,
                                     message_tokens=message_tokens,
                                     answer_tokens=answer_tokens,
                                     answer_text_list=answer_text_list,
                                     run_time=time.time() - workflow.context['start_time'],
                                     index=0)
        self.chat_info.append_chat_record(chat_record, self.client_id)
        # 重新设置缓存
        chat_cache.set(chat_id,
                       self.chat_info, timeout=60 * 30)
        if self.client_type == AuthenticationType.APPLICATION_ACCESS_TOKEN.value:
            application_public_access_client = QuerySet(ApplicationPublicAccessClient).filter(id=self.client_id).first()
            if application_public_access_client is not None:
                application_public_access_client.access_num = application_public_access_client.access_num + 1
                application_public_access_client.intraday_access_num = application_public_access_client.intraday_access_num + 1
                application_public_access_client.save()


class NodeResult:
    def __init__(self, node_variable: Dict, workflow_variable: Dict,
                 _write_context=write_context):
        self._write_context = _write_context
        self.node_variable = node_variable
        self.workflow_variable = workflow_variable

    def write_context(self, node, workflow):
        return self._write_context(self.node_variable, self.workflow_variable, node, workflow)

    def is_assertion_result(self):
        return 'branch_id' in self.node_variable


class ReferenceAddressSerializer(serializers.Serializer):
    node_id = serializers.CharField(required=True, error_messages=ErrMessage.char("节点id"))
    fields = serializers.ListField(
        child=serializers.CharField(required=True, error_messages=ErrMessage.char("节点字段")), required=True,
        error_messages=ErrMessage.list("节点字段数组"))


class FlowParamsSerializer(serializers.Serializer):
    # 历史对答
    history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                error_messages=ErrMessage.list("历史对答"))

    question = serializers.CharField(required=True, error_messages=ErrMessage.list("用户问题"))

    chat_id = serializers.CharField(required=True, error_messages=ErrMessage.list("对话id"))

    chat_record_id = serializers.CharField(required=True, error_messages=ErrMessage.char("对话记录id"))

    stream = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("流式输出"))

    client_id = serializers.CharField(required=False, error_messages=ErrMessage.char("客户端id"))

    client_type = serializers.CharField(required=False, error_messages=ErrMessage.char("客户端类型"))

    user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))
    re_chat = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("换个答案"))


class INode:

    @abstractmethod
    def save_context(self, details, workflow_manage):
        pass

    def get_answer_text(self):
        return self.answer_text

    def __init__(self, node, workflow_params, workflow_manage, runtime_node_id=None):
        # 当前步骤上下文,用于存储当前步骤信息
        self.status = 200
        self.err_message = ''
        self.node = node
        self.node_params = node.properties.get('node_data')
        self.workflow_params = workflow_params
        self.workflow_manage = workflow_manage
        self.node_params_serializer = None
        self.flow_params_serializer = None
        self.context = {}
        self.answer_text = None
        self.id = node.id
        if runtime_node_id is None:
            self.runtime_node_id = str(uuid.uuid1())
        else:
            self.runtime_node_id = runtime_node_id

    def valid_args(self, node_params, flow_params):
        flow_params_serializer_class = self.get_flow_params_serializer_class()
        node_params_serializer_class = self.get_node_params_serializer_class()
        if flow_params_serializer_class is not None and flow_params is not None:
            self.flow_params_serializer = flow_params_serializer_class(data=flow_params)
            self.flow_params_serializer.is_valid(raise_exception=True)
        if node_params_serializer_class is not None:
            self.node_params_serializer = node_params_serializer_class(data=node_params)
            self.node_params_serializer.is_valid(raise_exception=True)
        if self.node.properties.get('status', 200) != 200:
            raise ValidationError(ErrorDetail(f'节点{self.node.properties.get("stepName")} 不可用'))

    def get_reference_field(self, fields: List[str]):
        return self.get_field(self.context, fields)

    @staticmethod
    def get_field(obj, fields: List[str]):
        for field in fields:
            value = obj.get(field)
            if value is None:
                return None
            else:
                obj = value
        return obj

    @abstractmethod
    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        pass

    def get_flow_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FlowParamsSerializer

    def get_write_error_context(self, e):
        self.status = 500
        self.err_message = str(e)
        self.context['run_time'] = time.time() - self.context['start_time']

        def write_error_context(answer, status=200):
            pass

        return write_error_context

    def run(self) -> NodeResult:
        """
        :return: 执行结果
        """
        start_time = time.time()
        self.context['start_time'] = start_time
        result = self._run()
        self.context['run_time'] = time.time() - start_time
        return result

    def _run(self):
        result = self.execute()
        return result

    def execute(self, **kwargs) -> NodeResult:
        pass

    def get_details(self, index: int, **kwargs):
        """
        运行详情
        :return: 步骤详情
        """
        return {}
