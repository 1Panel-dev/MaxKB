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
    image_list = serializers.ListField(required=False, error_messages=ErrMessage.list("图片"))
    document_list = serializers.ListField(required=False, error_messages=ErrMessage.list("文档"))
    audio_list = serializers.ListField(required=False, error_messages=ErrMessage.list("音频"))
    child_node = serializers.DictField(required=False, allow_null=True, error_messages=ErrMessage.dict("子节点"))
    node_data = serializers.DictField(required=False, allow_null=True, error_messages=ErrMessage.dict("表单数据"))


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
        # 判断是否包含这个属性
        app_document_list = self.node_params_serializer.data.get('document_list', [])
        if app_document_list and len(app_document_list) > 0:
            app_document_list = self.workflow_manage.get_reference_field(
                app_document_list[0],
                app_document_list[1:])
            for document in app_document_list:
                if 'file_id' not in document:
                    raise ValueError("参数值错误: 上传的文档中缺少file_id，文档上传失败")
        app_image_list = self.node_params_serializer.data.get('image_list', [])
        if app_image_list and len(app_image_list) > 0:
            app_image_list = self.workflow_manage.get_reference_field(
                app_image_list[0],
                app_image_list[1:])
            for image in app_image_list:
                if 'file_id' not in image:
                    raise ValueError("参数值错误: 上传的图片中缺少file_id，图片上传失败")

        app_audio_list = self.node_params_serializer.data.get('audio_list', [])
        if app_audio_list and len(app_audio_list) > 0:
            app_audio_list = self.workflow_manage.get_reference_field(
                app_audio_list[0],
                app_audio_list[1:])
            for audio in app_audio_list:
                if 'file_id' not in audio:
                    raise ValueError("参数值错误: 上传的图片中缺少file_id，音频上传失败")
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                            app_document_list=app_document_list, app_image_list=app_image_list,
                            app_audio_list=app_audio_list,
                            message=str(question), **kwargs)

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat, client_id, client_type,
                app_document_list=None, app_image_list=None, app_audio_list=None, child_node=None, node_data=None,
                **kwargs) -> NodeResult:
        pass
