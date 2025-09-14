# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class ImageToVideoNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, label=_("Model id"))

    prompt = serializers.CharField(required=True, label=_("Prompt word (positive)"))

    negative_prompt = serializers.CharField(required=False, label=_("Prompt word (negative)"),
                                            allow_null=True, allow_blank=True, )
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=False, default=0,
                                               label=_("Number of multi-round conversations"))

    dialogue_type = serializers.CharField(required=False, default='NODE',
                                          label=_("Conversation storage type"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    model_params_setting = serializers.JSONField(required=False, default=dict,
                                                 label=_("Model parameter settings"))

    first_frame_url = serializers.ListField(required=True, label=_("First frame url"))
    last_frame_url = serializers.ListField(required=False, label=_("Last frame url"))


class IImageToVideoNode(INode):
    type = 'image-to-video-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ImageToVideoNodeSerializer

    def _run(self):
        first_frame_url = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('first_frame_url')[0],
            self.node_params_serializer.data.get('first_frame_url')[1:])
        if first_frame_url is []:
            raise ValueError(
                _("First frame url cannot be empty"))
        last_frame_url = None
        if self.node_params_serializer.data.get('last_frame_url') is not None and self.node_params_serializer.data.get(
                'last_frame_url') != []:
            last_frame_url = self.workflow_manage.get_reference_field(
                self.node_params_serializer.data.get('last_frame_url')[0],
                self.node_params_serializer.data.get('last_frame_url')[1:])
        node_params_data = {k: v for k, v in self.node_params_serializer.data.items()
                            if k not in ['first_frame_url', 'last_frame_url']}
        return self.execute(first_frame_url=first_frame_url, last_frame_url=last_frame_url,
                            **node_params_data, **self.flow_params_serializer.data)

    def execute(self, model_id, prompt, negative_prompt, dialogue_number, dialogue_type, history_chat_record, chat_id,
                model_params_setting,
                chat_record_id,
                first_frame_url, last_frame_url,
                **kwargs) -> NodeResult:
        pass
