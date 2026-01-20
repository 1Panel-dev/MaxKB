# coding=utf-8
from typing import Type

from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult

from django.utils.translation import gettext_lazy as _


class ApplicationNodeSerializer(serializers.Serializer):
    application_id = serializers.CharField(required=True, label=_("Application ID"))
    question_reference_address = serializers.ListField(required=True,
                                                       label=_("User Questions"))
    api_input_field_list = serializers.ListField(required=False, label=_("API Input Fields"))
    user_input_field_list = serializers.ListField(required=False,
                                                  label=_("User Input Fields"))
    image_list = serializers.ListField(required=False, label=_("picture"))
    document_list = serializers.ListField(required=False, label=_("document"))
    audio_list = serializers.ListField(required=False, label=_("Audio"))
    video_list = serializers.ListField(required=False, label=_("Video"))
    child_node = serializers.DictField(required=False, allow_null=True,
                                       label=_("Child Nodes"))
    node_data = serializers.DictField(required=False, allow_null=True, label=_("Form Data"))


class IApplicationNode(INode):
    type = 'application-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP]

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
        app_video_list = self.node_params_serializer.data.get('video_list', [])
        if app_video_list and len(app_video_list) > 0:
            app_video_list = self.workflow_manage.get_reference_field(
                app_video_list[0],
                app_video_list[1:]
            )
            for video in app_video_list:
                if 'file_id' not in video:
                    raise ValueError(
                        _("Parameter value error: The uploaded video lacks file_id, and the video upload fails."))
        return self.execute(**{**self.flow_params_serializer.data, **self.node_params_serializer.data},
                            app_document_list=app_document_list, app_image_list=app_image_list,
                            app_audio_list=app_audio_list,
                            app_video_list=app_video_list,
                            message=str(question), **kwargs)

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat, client_id, client_type,
                app_document_list=None, app_image_list=None, app_audio_list=None, app_video_list=None, child_node=None,
                node_data=None,
                **kwargs) -> NodeResult:
        pass
