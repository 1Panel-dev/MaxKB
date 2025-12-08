# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult

from django.utils.translation import gettext_lazy as _


class VideoUnderstandNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, label=_("Model id"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))

    dialogue_type = serializers.CharField(required=True, label=_("Conversation storage type"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    video_list = serializers.ListField(required=False, label=_("video"))

    model_params_setting = serializers.JSONField(required=False, default=dict,
                                                 label=_("Model parameter settings"))


class IVideoUnderstandNode(INode):
    type = 'video-understand-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VideoUnderstandNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('video_list')[0],
                                                       self.node_params_serializer.data.get('video_list')[1:])
        return self.execute(video=res, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, dialogue_type, history_chat_record, stream, chat_id,
                model_params_setting,
                chat_record_id,
                video,
                **kwargs) -> NodeResult:
        pass
