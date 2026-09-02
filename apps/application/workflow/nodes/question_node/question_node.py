# coding=utf-8
"""
@project: MaxKB
@file： question_node.py
@desc:
"""

import re
from functools import reduce

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, SystemMessage
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id, get_model_credential


class QuestionNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))


def _get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
    return model_params_setting


def _get_history_message(history_chat_record, dialogue_number):
    start_index = len(history_chat_record) - dialogue_number
    history_message = reduce(
        lambda x, y: [*x, *y],
        [
            [history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
            for index in range(start_index if start_index > 0 else 0, len(history_chat_record))
        ],
        [],
    )
    for message in history_message:
        if isinstance(message.content, str):
            message.content = re.sub(r"<form_rander>.*?</form_rander>", "", message.content, flags=re.DOTALL)
    return history_message


class QuestionNode(INode):
    serializer_class = QuestionNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "question-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        model_id = node_params.get("model_id")
        model_id_type = node_params.get("model_id_type", "custom")
        model_id_reference = node_params.get("model_id_reference")
        model_params_setting = node_params.get("model_params_setting")
        system = node_params.get("system", "")
        prompt = node_params.get("prompt", "")
        dialogue_number = node_params.get("dialogue_number", 0)
        is_result = node_params.get("is_result", False)

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
            workspace_id = workflow_params.get("workspace_id")
        else:
            history_chat_record = workflow_params.get("history_chat_record", [])
            workspace_id = workflow_params.get("workspace_id")

        if model_id_type == "reference" and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0],
                model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get("model_id", model_id)
                model_params_setting = reference_data.get("model_params_setting")

        if not model_id:
            raise Exception(_("Model is not allowed to be empty"))

        if model_params_setting is None and model_id:
            model_params_setting = _get_default_model_params_setting(model_id)

        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id, **(model_params_setting or {}))

        history_message = _get_history_message(history_chat_record, dialogue_number)
        self.write_context(
            "history_message",
            [{"content": message.content, "role": message.type} for message in (history_message or [])],
        )

        question = HumanMessage(self.workflow_manage.generate_prompt(prompt))
        self.write_context("question", question.content)

        system = self.workflow_manage.generate_prompt(system)
        self.write_context("system", system)

        if system and len(system) > 0:
            message_list = [SystemMessage(system), *history_message, question]
        else:
            message_list = [*history_message, question]
        self.write_context(
            "message_list",
            [{"content": m.content, "role": m.type} for m in message_list],
        )

        response = chat_model.stream(message_list)
        answer = ""

        for chunk in response:
            self._check_cancelled()
            answer += chunk.content

        message_tokens = chat_model.get_num_tokens_from_messages(message_list)
        answer_tokens = chat_model.get_num_tokens(answer)
        self.write_context("message_tokens", message_tokens)
        self.write_context("answer_tokens", answer_tokens)
        self.write_context("answer", answer)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(self.get_node_id(), answer, Status.SUCCESS, node_info, Position(self.get_node_id())))

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.get_context("question"),
                "answer": self.get_context("answer"),
                "system": self.get_context("system"),
                "message_tokens": self.get_context("message_tokens"),
                "answer_tokens": self.get_context("answer_tokens"),
                "history_message": self.get_context("history_message"),
            }
        )
        return details
