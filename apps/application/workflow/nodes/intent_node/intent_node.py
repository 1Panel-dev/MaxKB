# coding=utf-8
import json
import re
from typing import List, Dict, Any
from functools import reduce

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, SystemMessage
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.status import Status
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id, get_model_credential
from .prompt_template import PROMPT_TEMPLATE


class IntentBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Branch id"))
    content = serializers.CharField(required=True, label=_("content"))
    isOther = serializers.BooleanField(required=True, label=_("Branch Type"))


class IntentNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                               label=_("Reference Field"))
    content_list = serializers.ListField(required=True, label=_("Text content"))
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))
    branch = IntentBranchSerializer(many=True)


def _get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
    return model_params_setting


class IntentNode(INode):
    serializer_class = IntentNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'intent-node'

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        node_params = self.get_parameters()

        model_id = node_params.get('model_id')
        model_id_type = node_params.get('model_id_type', 'custom')
        model_id_reference = node_params.get('model_id_reference')
        content_list_ref = node_params.get('content_list')
        dialogue_number = node_params.get('dialogue_number', 0)
        model_params_setting = node_params.get('model_params_setting')
        branch = node_params.get('branch', [])

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
            workspace_id = workflow_params.get('workspace_id')
        else:
            history_chat_record = workflow_params.get('history_chat_record', [])
            workspace_id = workflow_params.get('workspace_id')

        if model_id_type == 'reference' and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0], model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get('model_id', model_id)
                model_params_setting = reference_data.get('model_params_setting')

        if not model_id:
            raise Exception(_('Model is not allowed to be empty'))

        if model_params_setting is None and model_id:
            model_params_setting = _get_default_model_params_setting(model_id)

        user_input = self.workflow_manage.get_reference_field(
            content_list_ref[0], content_list_ref[1:])

        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **(model_params_setting or {}))

        history_message = self._get_history_message(history_chat_record, dialogue_number)
        self.write_context('history_message', [
            {'content': message.content, 'role': message.type}
            for message in (history_message or [])
        ])

        self.write_context('user_input', str(user_input))

        prompt = self._build_classification_prompt(str(user_input), branch)
        system = self._build_system_prompt()
        message_list = self._generate_message_list(system, prompt, history_message)
        self.write_context('message_list', message_list)

        try:
            self._check_cancelled()
            r = chat_model.invoke(message_list)
            classification_result = r.content.strip()
            matched_branch = self._parse_classification_result(classification_result, branch)

            message_tokens = chat_model.get_num_tokens_from_messages(message_list)
            answer_tokens = chat_model.get_num_tokens(r.content)
            self.write_context('message_tokens', message_tokens)
            self.write_context('answer_tokens', answer_tokens)
            self.write_context('answer', r.content)
            self.write_context('branch_id', matched_branch['id'])
            self.write_context('reason', self._parse_result_reason(r.content))
            self.write_context('category', matched_branch.get('content', matched_branch['id']))

            self.complete(Status.SUCCESS, [self.branch_anchor(matched_branch['id'])])

        except Exception as e:
            other_branch = self._find_other_branch(branch)
            if other_branch:
                self.write_context('branch_id', other_branch['id'])
                self.write_context('category', other_branch.get('content', other_branch['id']))
                self.write_context('error', str(e))
                self.complete(Status.SUCCESS, [self.branch_anchor(other_branch['id'])])
            else:
                raise Exception(f"error: {str(e)}")

    def _get_history_message(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])

        for message in history_message:
            if isinstance(message.content, str):
                message.content = re.sub(r'<form_rander>.*?<\/form_rander>', '', message.content, flags=re.DOTALL)
        return history_message

    def _build_system_prompt(self) -> str:
        return "你是一个专业的意图识别助手，请根据用户输入和意图选项，准确识别用户的真实意图。"

    def _build_classification_prompt(self, user_input: str, branch: List[Dict]) -> str:
        classification_list = []
        other_branch = self._find_other_branch(branch)
        if other_branch:
            classification_list.append({
                "classificationId": 0,
                "content": other_branch.get('content')
            })
        classification_id = 1
        for b in branch:
            if not b.get('isOther'):
                classification_list.append({
                    "classificationId": classification_id,
                    "content": b['content']
                })
                classification_id += 1

        return PROMPT_TEMPLATE.format(
            classification_list=classification_list,
            user_input=user_input
        )

    def _generate_message_list(self, system: str, prompt: str, history_message):
        if system is None or len(system) == 0:
            return [*history_message, HumanMessage(self.workflow_manage.generate_prompt(prompt))]
        else:
            return [SystemMessage(self.workflow_manage.generate_prompt(system)), *history_message,
                    HumanMessage(self.workflow_manage.generate_prompt(prompt))]

    def _parse_classification_result(self, result: str, branch: List[Dict]) -> Dict[str, Any]:
        other_branch = self._find_other_branch(branch)
        normal_intents = [b for b in branch if not b.get('isOther')]

        def get_branch_by_id(category_id: int):
            if category_id == 0:
                return other_branch
            elif 1 <= category_id <= len(normal_intents):
                return normal_intents[category_id - 1]
            return None

        try:
            result_json = json.loads(result)
            classification_id = result_json.get('classificationId')
            matched_branch = get_branch_by_id(classification_id)
            if matched_branch:
                return matched_branch
        except Exception as e:
            numbers = re.findall(r'"classificationId":\s*(\d+)', result)
            if numbers:
                classification_id = int(numbers[0])
                matched_branch = get_branch_by_id(classification_id)
                if matched_branch:
                    return matched_branch

        return other_branch or (normal_intents[0] if normal_intents else {'id': 'unknown', 'content': 'unknown'})

    def _parse_result_reason(self, result: str):
        try:
            result_json = json.loads(result)
            return result_json.get('reason', '')
        except Exception as e:
            reason_patterns = [
                r'"reason":\s*"([^"]*)"',
                r'"reason":\s*"([^"]*)',
                r'"reason":\s*([^,}\n]*)',
            ]
            for pattern in reason_patterns:
                match = re.search(pattern, result, re.DOTALL)
                if match:
                    reason = match.group(1).strip()
                    reason = re.sub(r'["\s]*$', '', reason)
                    return reason
            return ''

    def _find_other_branch(self, branch: List[Dict]) -> Dict[str, Any] | None:
        for b in branch:
            if b.get('isOther'):
                return b
        return None
