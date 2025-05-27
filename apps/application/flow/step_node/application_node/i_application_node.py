# coding=utf-8
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage

from django.utils.translation import gettext_lazy as _


class ApplicationNodeSerializer(serializers.Serializer):
    application_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Application ID")))
    question_reference_address = serializers.ListField(required=True,
                                                       error_messages=ErrMessage.list(_("User Questions")))
    api_input_field_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("API Input Fields")))
    user_input_field_list = serializers.ListField(required=False,
                                                  error_messages=ErrMessage.uuid(_("User Input Fields")))
    image_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("picture")))
    document_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("document")))
    audio_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("Audio")))
    child_node = serializers.DictField(required=False, allow_null=True,
                                       error_messages=ErrMessage.dict(_("Child Nodes")))
    node_data = serializers.DictField(required=False, allow_null=True, error_messages=ErrMessage.dict(_("Form Data")))


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
            value = api_input_field.get('value', [''])[0] if api_input_field.get('value') else ''
            kwargs[api_input_field['variable']] = self.workflow_manage.get_reference_field(value,
                                                                                           api_input_field['value'][
                                                                                           1:]) if value != '' else ''

        for user_input_field in self.node_params_serializer.data.get('user_input_field_list', []):
            value = user_input_field.get('value', [''])[0] if user_input_field.get('value') else ''
            kwargs[user_input_field['field']] = self.workflow_manage.get_reference_field(value,
                                                                                         user_input_field['value'][
                                                                                         1:]) if value != '' else ''
        # 判断是否包含这个属性
        app_document_list = self.node_params_serializer.data.get('document_list', [])
        if app_document_list and len(app_document_list) > 0:
            app_document_list = self.workflow_manage.get_reference_field(
                app_document_list[0],
                app_document_list[1:])
            for document in app_document_list:
                if 'file_id' not in document:
                    raise ValueError(
                        _("Parameter value error: The uploaded document lacks file_id, and the document upload fails"))
        app_image_list = self.node_params_serializer.data.get('image_list', [])
        if app_image_list and len(app_image_list) > 0:
            app_image_list = self.workflow_manage.get_reference_field(
                app_image_list[0],
                app_image_list[1:])
            for image in app_image_list:
                if 'file_id' not in image:
                    raise ValueError(
                        _("Parameter value error: The uploaded image lacks file_id, and the image upload fails"))

        app_audio_list = self.node_params_serializer.data.get('audio_list', [])
        if app_audio_list and len(app_audio_list) > 0:
            app_audio_list = self.workflow_manage.get_reference_field(
                app_audio_list[0],
                app_audio_list[1:])
            for audio in app_audio_list:
                if 'file_id' not in audio:
                    raise ValueError(
                        _("Parameter value error: The uploaded audio lacks file_id, and the audio upload fails."))
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                            app_document_list=app_document_list, app_image_list=app_image_list,
                            app_audio_list=app_audio_list,
                            message=str(question), **kwargs)

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat, client_id, client_type,
                app_document_list=None, app_image_list=None, app_audio_list=None, child_node=None, node_data=None,
                **kwargs) -> NodeResult:
        pass
