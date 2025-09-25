# coding=utf-8
import json
import re
import time
import uuid
from typing import Dict, List
from django.utils.translation import gettext as _
from application.flow.common import Answer
from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.application_node.i_application_node import IApplicationNode
from application.models import Chat


def string_to_uuid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))


def _is_interrupt_exec(node, node_variable: Dict, workflow_variable: Dict):
    return node_variable.get('is_interrupt_exec', False)


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str,
                   reasoning_content: str):
    result = node_variable.get('result')
    node.context['application_node_dict'] = node_variable.get('application_node_dict')
    node.context['node_dict'] = node_variable.get('node_dict', {})
    node.context['is_interrupt_exec'] = node_variable.get('is_interrupt_exec')
    node.context['message_tokens'] = result.get('usage', {}).get('prompt_tokens', 0)
    node.context['answer_tokens'] = result.get('usage', {}).get('completion_tokens', 0)
    node.context['answer'] = answer
    node.context['result'] = answer
    node.context['reasoning_content'] = reasoning_content
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
    reasoning_content = ''
    usage = {}
    node_child_node = {}
    application_node_dict = node.context.get('application_node_dict', {})
    is_interrupt_exec = False
    for chunk in response:
        # 先把流转成字符串
        response_content = chunk.decode('utf-8')[6:]
        response_content = json.loads(response_content)
        content = (response_content.get('content', '') or '')
        runtime_node_id = response_content.get('runtime_node_id', '')
        chat_record_id = response_content.get('chat_record_id', '')
        child_node = response_content.get('child_node')
        view_type = response_content.get('view_type')
        node_type = response_content.get('node_type')
        real_node_id = response_content.get('real_node_id')
        node_is_end = response_content.get('node_is_end', False)
        _reasoning_content = (response_content.get('reasoning_content', '') or '')
        if node_type == 'form-node':
            is_interrupt_exec = True
        answer += content
        reasoning_content += _reasoning_content
        node_child_node = {'runtime_node_id': runtime_node_id, 'chat_record_id': chat_record_id,
                           'child_node': child_node}

        if real_node_id is not None:
            application_node = application_node_dict.get(real_node_id, None)
            if application_node is None:

                application_node_dict[real_node_id] = {'content': content,
                                                       'runtime_node_id': runtime_node_id,
                                                       'chat_record_id': chat_record_id,
                                                       'child_node': child_node,
                                                       'index': len(application_node_dict),
                                                       'view_type': view_type,
                                                       'reasoning_content': _reasoning_content}
            else:
                application_node['content'] += content
                application_node['reasoning_content'] += _reasoning_content

        yield {'content': content,
               'node_type': node_type,
               'runtime_node_id': runtime_node_id, 'chat_record_id': chat_record_id,
               'reasoning_content': _reasoning_content,
               'child_node': child_node,
               'real_node_id': real_node_id,
               'node_is_end': node_is_end,
               'view_type': view_type}
        usage = response_content.get('usage', {})
    node_variable['result'] = {'usage': usage}
    node_variable['is_interrupt_exec'] = is_interrupt_exec
    node_variable['child_node'] = node_child_node
    node_variable['application_node_dict'] = application_node_dict
    _write_context(node_variable, workflow_variable, node, workflow, answer, reasoning_content)


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
    reasoning_content = response.get('reasoning_content', '')
    answer_list = response.get('answer_list', [])
    node_variable['application_node_dict'] = {answer.get('real_node_id'): {**answer, 'index': index} for answer, index
                                              in
                                              zip(answer_list, range(len(answer_list)))}
    _write_context(node_variable, workflow_variable, node, workflow, answer, reasoning_content)


def reset_application_node_dict(application_node_dict, runtime_node_id, node_data):
    try:
        if application_node_dict is None:
            return
        for key in application_node_dict:
            application_node = application_node_dict[key]
            if application_node.get('runtime_node_id') == runtime_node_id:
                content: str = application_node.get('content')
                match = re.search('<form_rander>.*?</form_rander>', content)
                if match:
                    form_setting_str = match.group().replace('<form_rander>', '').replace('</form_rander>', '')
                    form_setting = json.loads(form_setting_str)
                    form_setting['is_submit'] = True
                    form_setting['form_data'] = node_data
                    value = f'<form_rander>{json.dumps(form_setting)}</form_rander>'
                    res = re.sub('<form_rander>.*?</form_rander>',
                                 '${value}', content)
                    application_node['content'] = res.replace('${value}', value)
    except Exception as e:
        pass


class BaseApplicationNode(IApplicationNode):
    def get_answer_list(self) -> List[Answer] | None:
        if self.answer_text is None:
            return None
        application_node_dict = self.context.get('application_node_dict')
        if application_node_dict is None or len(application_node_dict) == 0:
            return [
                Answer(self.answer_text, self.view_type, self.runtime_node_id, self.workflow_params['chat_record_id'],
                       self.context.get('child_node'), self.runtime_node_id, '')]
        else:
            return [Answer(n.get('content'), n.get('view_type'), self.runtime_node_id,
                           self.workflow_params['chat_record_id'], {'runtime_node_id': n.get('runtime_node_id'),
                                                                    'chat_record_id': n.get('chat_record_id')
                               , 'child_node': n.get('child_node')}, n.get('real_node_id'),
                           n.get('reasoning_content', ''))
                    for n in
                    sorted(application_node_dict.values(), key=lambda item: item.get('index'))]

    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['result'] = details.get('answer')
        self.context['question'] = details.get('question')
        self.context['type'] = details.get('type')
        self.context['reasoning_content'] = details.get('reasoning_content')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, application_id, message, chat_id, chat_record_id, stream, re_chat,
                chat_user_id,
                chat_user_type,
                app_document_list=None, app_image_list=None, app_audio_list=None, child_node=None, node_data=None,
                **kwargs) -> NodeResult:
        from chat.serializers.chat import ChatSerializers
        if application_id == self.workflow_manage.get_body().get('application_id'):
            raise Exception(_("The sub application cannot use the current node"))
        # 生成嵌入应用的chat_id
        current_chat_id = string_to_uuid(chat_id + application_id)
        Chat.objects.get_or_create(id=current_chat_id, defaults={
            'application_id': application_id,
            'abstract': message[0:1024],
            'chat_user_id': chat_user_id,
            'chat_user_type': chat_user_type
        })
        if app_document_list is None:
            app_document_list = []
        if app_image_list is None:
            app_image_list = []
        if app_audio_list is None:
            app_audio_list = []
        runtime_node_id = None
        record_id = None
        child_node_value = None
        if child_node is not None:
            runtime_node_id = child_node.get('runtime_node_id')
            record_id = child_node.get('chat_record_id')
            child_node_value = child_node.get('child_node')
            application_node_dict = self.context.get('application_node_dict')
            reset_application_node_dict(application_node_dict, runtime_node_id, node_data)
        response = ChatSerializers(data={
            "chat_id": current_chat_id,
            "chat_user_id": chat_user_id,
            'chat_user_type': chat_user_type,
            'application_id': application_id,
            'debug': False
        }).chat(instance=
                {'message': message,
                 're_chat': re_chat,
                 'stream': stream,
                 'document_list': app_document_list,
                 'image_list': app_image_list,
                 'audio_list': app_audio_list,
                 'runtime_node_id': runtime_node_id,
                 'chat_record_id': record_id,
                 'child_node': child_node_value,
                 'node_data': node_data,
                 'form_data': kwargs}
                )

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
            value = api_input_field.get('value', [''])[0] if api_input_field.get('value') else ''
            global_fields.append({
                'label': api_input_field['variable'],
                'key': api_input_field['variable'],
                'value': self.workflow_manage.get_reference_field(
                    value,
                    api_input_field['value'][1:]
                ) if value != '' else ''
            })

        for user_input_field in self.node_params_serializer.data.get('user_input_field_list', []):
            value = user_input_field.get('value', [''])[0] if user_input_field.get('value') else ''
            global_fields.append({
                'label': user_input_field['label'],
                'key': user_input_field['field'],
                'value': self.workflow_manage.get_reference_field(
                    value,
                    user_input_field['value'][1:]
                ) if value != '' else ''
            })
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "info": self.node.properties.get('node_data'),
            'run_time': self.context.get('run_time'),
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'reasoning_content': self.context.get('reasoning_content'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message,
            'global_fields': global_fields,
            'document_list': self.workflow_manage.document_list,
            'image_list': self.workflow_manage.image_list,
            'audio_list': self.workflow_manage.audio_list,
            'application_node_dict': self.context.get('application_node_dict')
        }
