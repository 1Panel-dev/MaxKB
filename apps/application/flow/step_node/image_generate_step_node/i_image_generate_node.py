# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class ImageGenerateNodeSerializer(serializers.Serializer):
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


class IImageGenerateNode(INode):
    type = 'image-generate-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ImageGenerateNodeSerializer

    def _run(self):
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                                **{'history_chat_record': [], 'stream': True, 'chat_id': None, 'chat_record_id': None})
        else:
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, prompt, negative_prompt, dialogue_number, dialogue_type, history_chat_record,
                model_params_setting,
                chat_record_id,
                **kwargs) -> NodeResult:
        pass
