# coding=utf-8
import json
import time
import uuid
from typing import Dict

from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.application_node.i_application_node import IApplicationNode
from application.models import Chat


def string_to_uuid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))


def _is_interrupt_exec(node, node_variable: Dict, workflow_variable: Dict):
    return node_variable.get('is_interrupt_exec', False)


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str):
    result = node_variable.get('result')
    node.context['child_node'] = node_variable.get('child_node')
    node.context['is_interrupt_exec'] = node_variable.get('is_interrupt_exec')
    node.context['message_tokens'] = result.get('usage', {}).get('prompt_tokens', 0)
    node.context['answer_tokens'] = result.get('usage', {}).get('completion_tokens', 0)
    node.context['answer'] = answer
    node.context['result'] = answer
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
    usage = {}
    node_child_node = {}
    is_interrupt_exec = False
    for chunk in response:
        # 先把流转成字符串
        response_content = chunk.decode('utf-8')[6:]
        response_content = json.loads(response_content)
        content = response_content.get('content', '')
        runtime_node_id = response_content.get('runtime_node_id', '')
        chat_record_id = response_content.get('chat_record_id', '')
        child_node = response_content.get('child_node')
        node_type = response_content.get('node_type')
        real_node_id = response_content.get('real_node_id')
        node_is_end = response_content.get('node_is_end', False)
        if node_type == 'form-node':
            is_interrupt_exec = True
        answer += content
        node_child_node = {'runtime_node_id': runtime_node_id, 'chat_record_id': chat_record_id,
                           'child_node': child_node}
        yield {'content': content,
               'node_type': node_type,
               'runtime_node_id': runtime_node_id, 'chat_record_id': chat_record_id,
               'child_node': child_node,
               'real_node_id': real_node_id,
               'node_is_end': node_is_end}
        usage = response_content.get('usage', {})
    node_variable['result'] = {'usage': usage}
    node_variable['is_interrupt_exec'] = is_interrupt_exec
    node_variable['child_node'] = node_child_node
    _write_context(node_variable, workflow_variable, node, workflow, answer)


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result', {}).get('data', {})
    node_variable['result'] = {'usage': {'completion_tokens': response.get('completion_tokens'),
                                         'prompt_tokens': response.get('prompt_tokens')}}
    answer = response.get('content', '') or "抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。"
    _write_context(node_variable, workflow_variable, node, workflow, answer)


class BaseApplicationNode(IApplicationNode):
    def get_answer_text(self):
        if self.answer_text is None:
            return None
        return {'content': self.answer_text, 'runtime_node_id': self.runtime_node_id,
                'chat_record_id': self.workflow_params['chat_record_id'], 'child_node': self.context.get('child_node')}

    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['question'] = details.get('question')
        self.context['type'] = details.get('type')
        self.answer_text = details.get('answer')

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat, client_id, client_type,
                app_document_list=None, app_image_list=None, child_node=None, node_data=None,
                **kwargs) -> NodeResult:
        from application.serializers.chat_message_serializers import ChatMessageSerializer
        # 生成嵌入应用的chat_id
        current_chat_id = string_to_uuid(chat_id + application_id)
        Chat.objects.get_or_create(id=current_chat_id, defaults={
            'application_id': application_id,
            'abstract': message
        })
        if app_document_list is None:
            app_document_list = []
        if app_image_list is None:
            app_image_list = []
        runtime_node_id = None
        record_id = None
        child_node_value = None
        if child_node is not None:
            runtime_node_id = child_node.get('runtime_node_id')
            record_id = child_node.get('chat_record_id')
            child_node_value = child_node.get('child_node')

        response = ChatMessageSerializer(
            data={'chat_id': current_chat_id, 'message': message,
                  're_chat': re_chat,
                  'stream': stream,
                  'application_id': application_id,
                  'client_id': client_id,
                  'client_type': client_type,
                  'document_list': app_document_list,
                  'image_list': app_image_list,
                  'runtime_node_id': runtime_node_id,
                  'chat_record_id': record_id,
                  'child_node': child_node_value,
                  'node_data': node_data,
                  'form_data': kwargs}).chat()
        if response.status_code == 200:
            if stream:
                content_generator = response.streaming_content
                return NodeResult({'result': content_generator, 'question': message}, {},
                                  _write_context=write_context_stream, _is_interrupt=_is_interrupt_exec)
            else:
                data = json.loads(response.content)
                return NodeResult({'result': data, 'question': message}, {},
                                  _write_context=write_context, _is_interrupt=_is_interrupt_exec)

    def get_details(self, index: int, **kwargs):
        global_fields = []
        for api_input_field in self.node_params_serializer.data.get('api_input_field_list', []):
            global_fields.append({
                'label': api_input_field['variable'],
                'key': api_input_field['variable'],
                'value': self.workflow_manage.get_reference_field(
                    api_input_field['value'][0],
                    api_input_field['value'][1:])
            })
        for user_input_field in self.node_params_serializer.data.get('user_input_field_list', []):
            global_fields.append({
                'label': user_input_field['label'],
                'key': user_input_field['field'],
                'value': self.workflow_manage.get_reference_field(
                    user_input_field['value'][0],
                    user_input_field['value'][1:])
            })
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "info": self.node.properties.get('node_data'),
            'run_time': self.context.get('run_time'),
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message,
            'global_fields': global_fields,
            'document_list': self.workflow_manage.document_list,
            'image_list': self.workflow_manage.image_list
        }
