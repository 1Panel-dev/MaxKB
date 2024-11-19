# coding=utf-8
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class ApplicationNodeSerializer(serializers.Serializer):
    application_id = serializers.CharField(required=True, error_messages=ErrMessage.char("应用id"))
    question_reference_address = serializers.ListField(required=True, error_messages=ErrMessage.list("用户问题"))
    api_input_field_list = serializers.ListField(required=False, error_messages=ErrMessage.list("api输入字段"))
    user_input_field_list = serializers.ListField(required=False, error_messages=ErrMessage.uuid("用户输入字段"))


class IApplicationNode(INode):
    type = 'application-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ApplicationNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('question_reference_address')[0],
            self.node_params_serializer.data.get('question_reference_address')[1:])
        kwargs = {}
        for api_input_field in self.node_params_serializer.data.get('api_input_field_list', []):
            kwargs[api_input_field['variable']] = self.workflow_manage.get_reference_field(api_input_field['value'][0],
                                                                                           api_input_field['value'][1:])
        for user_input_field in self.node_params_serializer.data.get('user_input_field_list', []):
            kwargs[user_input_field['field']] = self.workflow_manage.get_reference_field(user_input_field['value'][0],
                                                                                         user_input_field['value'][1:])

        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                            message=str(question), **kwargs)

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat, client_id, client_type,
                **kwargs) -> NodeResult:
        pass
