# coding=utf-8
import base64
import os
import time
from functools import reduce
from typing import List, Dict

from django.db.models import QuerySet
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.image_understand_step_node.i_image_understand_node import IImageUnderstandNode
from dataset.models import File
from setting.models_provider.tools import get_model_instance_by_model_user_id


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str):
    chat_model = node_variable.get('chat_model')
    message_tokens = node_variable['usage_metadata']['output_tokens'] if 'usage_metadata' in node_variable else 0
    answer_tokens = chat_model.get_num_tokens(answer)
    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['question'] = node_variable['question']
    node.context['run_time'] = time.time() - node.context['start_time']
    if workflow.is_result(node, NodeResult(node_variable, workflow_variable)):
        node.answer_text = answer


def write_context_stream(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据 (流式)
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    answer = ''
    for chunk in response:
        answer += chunk.content
        yield chunk.content
    _write_context(node_variable, workflow_variable, node, workflow, answer)


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    answer = response.content
    _write_context(node_variable, workflow_variable, node, workflow, answer)


class BaseImageUnderstandNode(IImageUnderstandNode):
    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['question'] = details.get('question')
        self.answer_text = details.get('answer')

    def execute(self, model_id, system, prompt, dialogue_number, dialogue_type, history_chat_record, stream, chat_id, chat_record_id,
                image,
                **kwargs) -> NodeResult:
        image_model = get_model_instance_by_model_user_id(model_id, self.flow_params_serializer.data.get('user_id'))
        history_message = self.get_history_message(history_chat_record, dialogue_number)
        self.context['history_message'] = history_message
        question = self.generate_prompt_question(prompt)
        self.context['question'] = question.content
        message_list = self.generate_message_list(image_model, system, prompt, history_message, image)
        self.context['message_list'] = message_list
        self.context['image_list'] = image
        self.context['dialogue_type'] = dialogue_type
        if stream:
            r = image_model.stream(message_list)
            return NodeResult({'result': r, 'chat_model': image_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context_stream)
        else:
            r = image_model.invoke(message_list)
            return NodeResult({'result': r, 'chat_model': image_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context)

    def get_history_message(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [self.generate_history_human_message(history_chat_record[index]), history_chat_record[index].get_ai_message()]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        return history_message

    def generate_history_human_message(self, chat_record):

        for data in chat_record.details.values():
            if self.node.id == data['node_id'] and 'image_list' in data:
                image_list = data['image_list']
                if len(image_list) == 0 or data['dialogue_type'] == 'WORKFLOW':
                    return HumanMessage(content=chat_record.problem_text)
                file_id = image_list[0]['file_id']
                file = QuerySet(File).filter(id=file_id).first()
                base64_image = base64.b64encode(file.get_byte()).decode("utf-8")
                return HumanMessage(
                    content=[
                        {'type': 'text', 'text': data['question']},
                        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}},
                    ])
        return HumanMessage(content=chat_record.problem_text)

    def generate_prompt_question(self, prompt):
        return HumanMessage(self.workflow_manage.generate_prompt(prompt))

    def generate_message_list(self, image_model, system: str, prompt: str, history_message, image):
        if image is not None and len(image) > 0:
            # 处理多张图片
            images = []
            for img in image:
                file_id = img['file_id']
                file = QuerySet(File).filter(id=file_id).first()
                base64_image = base64.b64encode(file.get_byte()).decode("utf-8")
                images.append({'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}})
            messages = [HumanMessage(
                content=[
                    {'type': 'text', 'text': self.workflow_manage.generate_prompt(prompt)},
                    *images
                ])]
        else:
            messages = [HumanMessage(self.workflow_manage.generate_prompt(prompt))]

        if system is not None and len(system) > 0:
            return [
                SystemMessage(self.workflow_manage.generate_prompt(system)),
                *history_message,
                *messages
            ]
        else:
            return [
                *history_message,
                *messages
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
            'system': self.node_params.get('system'),
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
            'dialogue_type': self.context.get('dialogue_type')
        }
