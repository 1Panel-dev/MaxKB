# coding=utf-8
from functools import reduce
from typing import List

import requests
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from application.flow.common import WorkflowMode
from application.flow.i_step_node import NodeResult
from application.flow.step_node.text_to_video_step_node.i_text_to_video_node import ITextToVideoNode
from common.utils.common import bytes_to_uploaded_file
from knowledge.models import FileSourceType
from oss.serializers.file import FileSerializer
from models_provider.tools import get_model_instance_by_model_workspace_id
from django.utils.translation import gettext


class BaseTextToVideoNode(ITextToVideoNode):
    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['exception_message'] = details.get('err_message')
        self.context['question'] = details.get('question')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, model_id, prompt, negative_prompt, dialogue_number, dialogue_type, history_chat_record,
                model_params_setting,
                chat_record_id,
                **kwargs) -> NodeResult:
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        ttv_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                             **model_params_setting)
        history_message = self.get_history_message(history_chat_record, dialogue_number)
        self.context['history_message'] = history_message
        question = self.generate_prompt_question(prompt)
        self.context['question'] = question
        message_list = self.generate_message_list(question, history_message)
        self.context['message_list'] = message_list
        self.context['dialogue_type'] = dialogue_type
        self.context['negative_prompt'] = self.generate_prompt_question(negative_prompt)
        video_urls = ttv_model.generate_video(question, negative_prompt)
        # 保存图片
        if video_urls is None:
            return NodeResult({'answer': gettext('Failed to generate video')}, {})
        file_name = 'generated_video.mp4'
        if isinstance(video_urls, str) and video_urls.startswith('http'):
            video_urls = requests.get(video_urls).content
        file = bytes_to_uploaded_file(video_urls, file_name)
        file_url = self.upload_file(file)
        video_label = f'<video src="{file_url}" controls style="max-width: 100%; width: 100%; height: auto;"></video>'
        video_list = [{'file_id': file_url.split('/')[-1], 'file_name': file_name, 'url': file_url}]
        return NodeResult({'answer': video_label, 'chat_model': ttv_model, 'message_list': message_list,
                           'video': video_list,
                           'history_message': history_message, 'question': question}, {})

    def upload_file(self, file):
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            return self.upload_knowledge_file(file)
        return self.upload_application_file(file)

    def upload_knowledge_file(self, file):
        knowledge_id = self.workflow_params.get('knowledge_id')
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

    def upload_application_file(self, file):
        application = self.workflow_manage.work_flow_post_handler.chat_info.application
        chat_id = self.workflow_params.get('chat_id')
        meta = {
            'debug': False if application.id else True,
            'chat_id': chat_id,
            'application_id': str(application.id) if application.id else None,
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': meta['application_id'],
            'source_type': FileSourceType.APPLICATION.value
        }).upload()
        return file_url

    def generate_history_ai_message(self, chat_record):
        for val in chat_record.details.values():
            if self.node.id == val['node_id'] and 'image_list' in val:
                if val['dialogue_type'] == 'WORKFLOW':
                    return chat_record.get_ai_message()
                image_list = val['image_list']
                return AIMessage(content=[
                    *[{'type': 'image_url', 'image_url': {'url': f'{file_url}'}} for file_url in image_list]
                ])
        return chat_record.get_ai_message()

    def get_history_message(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [self.generate_history_human_message(history_chat_record[index]),
             self.generate_history_ai_message(history_chat_record[index])]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        return history_message

    def generate_history_human_message(self, chat_record):

        for data in chat_record.details.values():
            if self.node.id == data['node_id'] and 'image_list' in data:
                image_list = data['image_list']
                if len(image_list) == 0 or data['dialogue_type'] == 'WORKFLOW':
                    return HumanMessage(content=chat_record.problem_text)
                return HumanMessage(content=data['question'])
        return HumanMessage(content=chat_record.problem_text)

    def generate_prompt_question(self, prompt):
        return self.workflow_manage.generate_prompt(prompt)

    def generate_message_list(self, question: str, history_message):
        return [
            *history_message,
            question
        ]

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else 'ai', 'content': message.content} for
                  message
                  in
                  message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'history_message': [{'content': message.content, 'role': message.type} for message in
                                (self.context.get('history_message') if self.context.get(
                                    'history_message') is not None else [])],
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message,
            'image_list': self.context.get('image_list'),
            'dialogue_type': self.context.get('dialogue_type'),
            'negative_prompt': self.context.get('negative_prompt'),
            'enableException': self.node.properties.get('enableException'),
        }
