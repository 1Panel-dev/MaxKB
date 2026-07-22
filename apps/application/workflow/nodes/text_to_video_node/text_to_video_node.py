# coding=utf-8
import uuid_utils.compat as uuid
import requests
from functools import reduce
from typing import List

from django.utils.translation import gettext_lazy as _, gettext
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.utils.common import bytes_to_uploaded_file
from knowledge.models import FileSourceType
from oss.serializers.file import FileSerializer
from models_provider.tools import get_model_instance_by_model_workspace_id
from common.utils.logger import maxkb_logger


class TextToVideoNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                               label=_("Reference Field"))
    prompt = serializers.CharField(required=True, label=_("Prompt word (positive)"))
    negative_prompt = serializers.CharField(required=False, label=_("Prompt word (negative)"),
                                            allow_null=True, allow_blank=True)
    dialogue_number = serializers.IntegerField(required=False, default=0,
                                               label=_("Number of multi-round conversations"))
    dialogue_type = serializers.CharField(required=False, default='NODE',
                                          label=_("Conversation storage type"))
    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))
    model_params_setting = serializers.JSONField(required=False, default=dict,
                                                 label=_("Model parameter settings"))


class TextToVideoNode(INode):
    serializer_class = TextToVideoNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'text-to-video-node'

    def execute(self):
        maxkb_logger.info(f'[TextToVideoNode] execute START, node_id={self.get_node_id()}')
        workflow_params = self.get_workflow_parameters()
        node_params = self.get_parameters()

        model_id = node_params.get('model_id')
        model_id_type = node_params.get('model_id_type', 'custom')
        model_id_reference = node_params.get('model_id_reference')
        prompt = node_params.get('prompt', '')
        negative_prompt = node_params.get('negative_prompt', '')
        dialogue_number = node_params.get('dialogue_number', 0)
        dialogue_type = node_params.get('dialogue_type', 'NODE')
        is_result = node_params.get('is_result', False)
        model_params_setting = node_params.get('model_params_setting')

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
            chat_id = None
            chat_record_id = None
            workspace_id = workflow_params.get('workspace_id')
        else:
            history_chat_record = workflow_params.get('history_chat_record', [])
            chat_id = workflow_params.get('chat_id')
            chat_record_id = workflow_params.get('chat_record_id')
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

        ttv_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                             **(model_params_setting or {}))

        history_message = self._get_history_message(history_chat_record, dialogue_number)
        self.write_context('history_message', [
            {'content': message.content, 'role': message.type}
            for message in (history_message or [])
        ])

        question = self.workflow_manage.generate_prompt(prompt)
        self.write_context('question', question)

        message_list = [*history_message, question]
        self.write_context('message_list', message_list)
        self.write_context('dialogue_type', dialogue_type)
        self.write_context('negative_prompt', self.workflow_manage.generate_prompt(negative_prompt))

        video_urls = ttv_model.generate_video(question, negative_prompt)
        maxkb_logger.info(f'[TextToVideoNode] generate_video result: {video_urls is not None}, node_id={self.get_node_id()}')

        if video_urls is None or video_urls == '':
            raise Exception(gettext('Failed to generate video'))

        file_name = 'generated_video.mp4'
        if isinstance(video_urls, str) and video_urls.startswith('http'):
            video_urls = requests.get(video_urls).content

        file = bytes_to_uploaded_file(video_urls, file_name)
        file_url = self._upload_file(file, workflow_type, workflow_params)

        video_label = f'<video src="{file_url}" controls style="max-width: 100%; width: 100%; height: auto; max-height: 60vh;"></video>'
        video_list = [{'file_id': file_url.split('/')[-1], 'file_name': file_name, 'url': file_url}]

        self.write_context('answer', video_label)
        self.write_context('video', video_list)
        self.write_context('chat_model', ttv_model)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(str(uuid.uuid7()), video_label, Status.SUCCESS, node_info, Position(self.get_node_id())))

    def _upload_file(self, file, workflow_type, workflow_params):
        if workflow_type == WorkflowType.KNOWLEDGE:
            return self._upload_knowledge_file(file, workflow_params)
        if workflow_type == WorkflowType.TOOL:
            return self._upload_tool_file(file, workflow_params)
        return self._upload_application_file(file, workflow_params)

    def _upload_knowledge_file(self, file, workflow_params):
        knowledge_id = workflow_params.get('knowledge_id')
        meta = {
            'debug': False,
            'knowledge_id': knowledge_id
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': knowledge_id,
            'source_type': FileSourceType.KNOWLEDGE.value
        }).upload()
        return file_url

    def _upload_tool_file(self, file, workflow_params):
        tool_id = workflow_params.get('tool_id')
        meta = {
            'debug': False,
            'tool_id': tool_id,
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': tool_id,
            'source_type': FileSourceType.TOOL.value
        }).upload()
        return file_url

    def _upload_application_file(self, file, workflow_params):
        application_id = workflow_params.get('application_id')
        chat_id = workflow_params.get('chat_id')
        debug = workflow_params.get('debug', False)
        meta = {
            'debug': debug,
            'chat_id': chat_id,
            'application_id': application_id,
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': application_id,
            'source_type': FileSourceType.APPLICATION.value
        }).upload()
        return file_url

    def _generate_history_ai_message(self, chat_record):
        for val in chat_record.details.values():
            if self.node.id == val['node_id'] and 'image_list' in val:
                if val['dialogue_type'] == 'WORKFLOW':
                    return chat_record.get_ai_message()
                image_list = val['image_list']
                return AIMessage(content=[
                    *[{'type': 'image_url', 'image_url': {'url': f'{file_url}'}} for file_url in image_list]
                ])
        return chat_record.get_ai_message()

    def _get_history_message(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [self._generate_history_human_message(history_chat_record[index]),
             self._generate_history_ai_message(history_chat_record[index])]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        return history_message

    def _generate_history_human_message(self, chat_record):
        for data in chat_record.details.values():
            if self.node.id == data['node_id'] and 'image_list' in data:
                image_list = data['image_list']
                if len(image_list) == 0 or data['dialogue_type'] == 'WORKFLOW':
                    return HumanMessage(content=chat_record.problem_text)
                return HumanMessage(content=data['question'])
        return HumanMessage(content=chat_record.problem_text)

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else 'ai', 'content': message.content} for
                  message in message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result
