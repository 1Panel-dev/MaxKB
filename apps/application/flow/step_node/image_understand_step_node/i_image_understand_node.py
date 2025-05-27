# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _


class ImageUnderstandNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Model id")))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   error_messages=ErrMessage.char(_("Role Setting")))
    prompt = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Prompt word")))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer(_("Number of multi-round conversations")))

    dialogue_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Conversation storage type")))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_('Whether to return content')))

    image_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("picture")))

    model_params_setting = serializers.JSONField(required=False, default=dict,
                                                 error_messages=ErrMessage.json(_("Model parameter settings")))


class IImageUnderstandNode(INode):
    type = 'image-understand-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ImageUnderstandNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('image_list')[0],
                                                       self.node_params_serializer.data.get('image_list')[1:])
        return self.execute(image=res, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, dialogue_type, history_chat_record, stream, chat_id,
                model_params_setting,
                chat_record_id,
                image,
                **kwargs) -> NodeResult:
        pass
