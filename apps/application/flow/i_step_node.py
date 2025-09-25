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
from hashlib import sha1
from typing import Type, Dict, List

from django.core import cache
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail

from application.flow.common import Answer, NodeChunk
from application.models import ApplicationChatUserStats
from application.models import ChatRecord, ChatUserType
from common.field.common import InstanceField

chat_cache = cache


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


def is_interrupt(node, step_variable: Dict, global_variable: Dict):
    return node.type == 'form-node' and not node.context.get('is_submit', False)


class WorkFlowPostHandler:
    def __init__(self, chat_info):
        self.chat_info = chat_info

    def handler(self, workflow):
        workflow_body = workflow.get_body()
        question = workflow_body.get('question')
        chat_record_id = workflow_body.get('chat_record_id')
        chat_id = workflow_body.get('chat_id')
        details = workflow.get_runtime_details()
        message_tokens = sum([row.get('message_tokens') for row in details.values() if
                              'message_tokens' in row and row.get('message_tokens') is not None])
        answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                             'answer_tokens' in row and row.get('answer_tokens') is not None])
        answer_text_list = workflow.get_answer_text_list()
        answer_text = '\n\n'.join(
            '\n\n'.join([a.get('content') for a in answer]) for answer in
            answer_text_list)
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

        self.chat_info.append_chat_record(chat_record)
        self.chat_info.set_cache()

        if not self.chat_info.debug and [ChatUserType.ANONYMOUS_USER.value, ChatUserType.CHAT_USER.value].__contains__(
                workflow_body.get('chat_user_type')):
            application_public_access_client = (QuerySet(ApplicationChatUserStats)
                                                .filter(chat_user_id=workflow_body.get('chat_user_id'),
                                                        chat_user_type=workflow_body.get('chat_user_type'),
                                                        application_id=self.chat_info.application_id).first())
            if application_public_access_client is not None:
                application_public_access_client.access_num = application_public_access_client.access_num + 1
                application_public_access_client.intraday_access_num = application_public_access_client.intraday_access_num + 1
                application_public_access_client.save()


class NodeResult:
    def __init__(self, node_variable: Dict, workflow_variable: Dict,
                 _write_context=write_context, _is_interrupt=is_interrupt):
        self._write_context = _write_context
        self.node_variable = node_variable
        self.workflow_variable = workflow_variable
        self._is_interrupt = _is_interrupt

    def write_context(self, node, workflow):
        return self._write_context(self.node_variable, self.workflow_variable, node, workflow)

    def is_assertion_result(self):
        return 'branch_id' in self.node_variable

    def is_interrupt_exec(self, current_node):
        """
        是否中断执行
        @param current_node:
        @return:
        """
        return self._is_interrupt(current_node, self.node_variable, self.workflow_variable)


class ReferenceAddressSerializer(serializers.Serializer):
    node_id = serializers.CharField(required=True, label="节点id")
    fields = serializers.ListField(
        child=serializers.CharField(required=True, label="节点字段"), required=True,
        label="节点字段数组")


class FlowParamsSerializer(serializers.Serializer):
    # 历史对答
    history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                label="历史对答")

    question = serializers.CharField(required=True, label="用户问题")

    chat_id = serializers.CharField(required=True, label="对话id")

    chat_record_id = serializers.CharField(required=True, label="对话记录id")

    stream = serializers.BooleanField(required=True, label="流式输出")

    chat_user_id = serializers.CharField(required=False, label="对话用户id")

    chat_user_type = serializers.CharField(required=False, label="对话用户类型")

    workspace_id = serializers.CharField(required=True, label="工作空间id")

    application_id = serializers.CharField(required=True, label="应用id")

    re_chat = serializers.BooleanField(required=True, label="换个答案")

    debug = serializers.BooleanField(required=True, label="是否debug")


class INode:
    view_type = 'many_view'

    @abstractmethod
    def save_context(self, details, workflow_manage):
        pass

    def get_answer_list(self) -> List[Answer] | None:
        if self.answer_text is None:
            return None
        reasoning_content_enable = self.context.get('model_setting', {}).get('reasoning_content_enable', False)
        return [
            Answer(self.answer_text, self.view_type, self.runtime_node_id, self.workflow_params['chat_record_id'], {},
                   self.runtime_node_id, self.context.get('reasoning_content', '') if reasoning_content_enable else '')]

    def __init__(self, node, workflow_params, workflow_manage, up_node_id_list=None,
                 get_node_params=lambda node: node.properties.get('node_data'), salt=None):
        # 当前步骤上下文,用于存储当前步骤信息
        self.status = 200
        self.err_message = ''
        self.node = node
        self.node_params = get_node_params(node)
        self.workflow_params = workflow_params
        self.workflow_manage = workflow_manage
        self.node_params_serializer = None
        self.flow_params_serializer = None
        self.context = {}
        self.answer_text = None
        self.id = node.id
        if up_node_id_list is None:
            up_node_id_list = []
        self.up_node_id_list = up_node_id_list
        self.node_chunk = NodeChunk()
        self.runtime_node_id = sha1(uuid.NAMESPACE_DNS.bytes + bytes(str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                                                    "".join([*sorted(up_node_id_list),
                                                                                             node.id]))),
                                                                     "utf-8")).hexdigest() + (
                                   "__" + str(salt) if salt is not None else '')

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
        self.answer_text = str(e)
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
