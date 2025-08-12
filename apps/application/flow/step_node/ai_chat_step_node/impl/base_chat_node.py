# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_question_node.py
    @date：2024/6/4 14:30
    @desc:
"""
import asyncio
import json
import os
import re
import time
from functools import reduce
from typing import List, Dict

from django.db.models import QuerySet
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.ai_chat_step_node.i_chat_node import IChatNode
from application.flow.tools import Reasoning
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model
from models_provider.tools import get_model_credential, get_model_instance_by_model_workspace_id
from tools.models import Tool

tool_message_template = """
<details>
    <summary>
        <strong>Called MCP Tool: <em>%s</em></strong>
    </summary>

%s

</details>

"""

tool_message_json_template = """
```json
%s
```
"""


def generate_tool_message_template(name, context):
    if '```' in context:
        return tool_message_template % (name, context)
    else:
        return tool_message_template % (name, tool_message_json_template % (context))


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str,
                   reasoning_content: str):
    chat_model = node_variable.get('chat_model')
    message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
    answer_tokens = chat_model.get_num_tokens(answer)
    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['question'] = node_variable['question']
    node.context['run_time'] = time.time() - node.context['start_time']
    node.context['reasoning_content'] = reasoning_content
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
    model_setting = node.context.get('model_setting',
                                     {'reasoning_content_enable': False, 'reasoning_content_end': '</think>',
                                      'reasoning_content_start': '<think>'})
    reasoning = Reasoning(model_setting.get('reasoning_content_start', '<think>'),
                          model_setting.get('reasoning_content_end', '</think>'))
    response_reasoning_content = False

    for chunk in response:
        reasoning_chunk = reasoning.get_reasoning_content(chunk)
        content_chunk = reasoning_chunk.get('content')
        if 'reasoning_content' in chunk.additional_kwargs:
            response_reasoning_content = True
            reasoning_content_chunk = chunk.additional_kwargs.get('reasoning_content', '')
        else:
            reasoning_content_chunk = reasoning_chunk.get('reasoning_content')
        answer += content_chunk
        if reasoning_content_chunk is None:
            reasoning_content_chunk = ''
        reasoning_content += reasoning_content_chunk
        yield {'content': content_chunk,
               'reasoning_content': reasoning_content_chunk if model_setting.get('reasoning_content_enable',
                                                                                 False) else ''}

    reasoning_chunk = reasoning.get_end_reasoning_content()
    answer += reasoning_chunk.get('content')
    reasoning_content_chunk = ""
    if not response_reasoning_content:
        reasoning_content_chunk = reasoning_chunk.get(
            'reasoning_content')
    yield {'content': reasoning_chunk.get('content'),
           'reasoning_content': reasoning_content_chunk if model_setting.get('reasoning_content_enable',
                                                                             False) else ''}
    _write_context(node_variable, workflow_variable, node, workflow, answer, reasoning_content)


async def _yield_mcp_response(chat_model, message_list, mcp_servers):
    client = MultiServerMCPClient(json.loads(mcp_servers))
    tools = await client.get_tools()
    agent = create_react_agent(chat_model, tools)
    response = agent.astream({"messages": message_list}, stream_mode='messages')
    async for chunk in response:
        if isinstance(chunk[0], ToolMessage):
            content = generate_tool_message_template(chunk[0].name, chunk[0].content)
            chunk[0].content = content
            yield chunk[0]
        if isinstance(chunk[0], AIMessageChunk):
            yield chunk[0]


def mcp_response_generator(chat_model, message_list, mcp_servers):
    loop = asyncio.new_event_loop()
    try:
        async_gen = _yield_mcp_response(chat_model, message_list, mcp_servers)
        while True:
            try:
                chunk = loop.run_until_complete(anext_async(async_gen))
                yield chunk
            except StopAsyncIteration:
                break
    except Exception as e:
        maxkb_logger.error(f'Exception: {e}')
    finally:
        loop.close()


async def anext_async(agen):
    return await agen.__anext__()


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    model_setting = node.context.get('model_setting',
                                     {'reasoning_content_enable': False, 'reasoning_content_end': '</think>',
                                      'reasoning_content_start': '<think>'})
    reasoning = Reasoning(model_setting.get('reasoning_content_start'), model_setting.get('reasoning_content_end'))
    reasoning_result = reasoning.get_reasoning_content(response)
    reasoning_result_end = reasoning.get_end_reasoning_content()
    content = reasoning_result.get('content') + reasoning_result_end.get('content')
    meta = {**response.response_metadata, **response.additional_kwargs}
    if 'reasoning_content' in meta:
        reasoning_content = meta.get('reasoning_content', '')
    else:
        reasoning_content = reasoning_result.get('reasoning_content') + reasoning_result_end.get('reasoning_content')
    _write_context(node_variable, workflow_variable, node, workflow, content, reasoning_content)


def get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(
        model.model_name).get_default_form_data()
    return model_params_setting


def get_node_message(chat_record, runtime_node_id):
    node_details = chat_record.get_node_details_runtime_node_id(runtime_node_id)
    if node_details is None:
        return []
    return [HumanMessage(node_details.get('question')), AIMessage(node_details.get('answer'))]


def get_workflow_message(chat_record):
    return [chat_record.get_human_message(), chat_record.get_ai_message()]


def get_message(chat_record, dialogue_type, runtime_node_id):
    return get_node_message(chat_record, runtime_node_id) if dialogue_type == 'NODE' else get_workflow_message(
        chat_record)


class BaseChatNode(IChatNode):
    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['question'] = details.get('question')
        self.context['reasoning_content'] = details.get('reasoning_content')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id, chat_record_id,
                model_params_setting=None,
                dialogue_type=None,
                model_setting=None,
                mcp_enable=False,
                mcp_servers=None,
                mcp_tool_id=None,
                mcp_source=None,
                tool_enable=False,
                tool_ids=None,
                **kwargs) -> NodeResult:
        if dialogue_type is None:
            dialogue_type = 'WORKFLOW'

        if model_params_setting is None:
            model_params_setting = get_default_model_params_setting(model_id)
        if model_setting is None:
            model_setting = {'reasoning_content_enable': False, 'reasoning_content_end': '</think>',
                             'reasoning_content_start': '<think>'}
        self.context['model_setting'] = model_setting
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **model_params_setting)
        history_message = self.get_history_message(history_chat_record, dialogue_number, dialogue_type,
                                                   self.runtime_node_id)
        self.context['history_message'] = history_message
        question = self.generate_prompt_question(prompt)
        self.context['question'] = question.content
        system = self.workflow_manage.generate_prompt(system)
        self.context['system'] = system
        message_list = self.generate_message_list(system, prompt, history_message)
        self.context['message_list'] = message_list

        # 处理 MCP 请求
        mcp_result = self._handle_mcp_request(
            mcp_enable, tool_enable, mcp_source, mcp_servers, mcp_tool_id, tool_ids, chat_model, message_list,
            history_message, question
        )
        if mcp_result:
            return mcp_result

        if stream:
            r = chat_model.stream(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context_stream)
        else:
            r = chat_model.invoke(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context)

    def _handle_mcp_request(self, mcp_enable, tool_enable, mcp_source, mcp_servers, mcp_tool_id, tool_ids,
                            chat_model, message_list, history_message, question):
        if not mcp_enable and not tool_enable:
            return None

        mcp_servers_config = {}

        if mcp_enable:
            if mcp_source == 'custom' and mcp_servers is not None and '"stdio"' not in mcp_servers:
                mcp_servers_config = json.loads(mcp_servers)
            elif mcp_tool_id:
                mcp_tool = QuerySet(Tool).filter(id=mcp_tool_id).first()
                if mcp_tool:
                    mcp_servers_config = json.loads(mcp_tool.code)

        if tool_enable:
            if tool_ids and len(tool_ids) > 0:  # 如果有工具ID，则将其转换为MCP
                self.context['tool_ids'] = tool_ids
                for tool_id in tool_ids:
                    tool = QuerySet(Tool).filter(id=tool_id).first()
                    executor = ToolExecutor()
                    code = executor.get_exec_code(tool.code)
                    code_path = f'{executor.sandbox_path}/execute/{tool_id}.py'
                    with open(code_path, 'w') as f:
                        f.write(code)

                    tool_config = {
                        'command': 'python',
                        'args': [code_path],
                        'transport': 'stdio',
                    }
                    mcp_servers_config[str(tool.id)] = tool_config

        if len(mcp_servers_config) > 0:
            r = mcp_response_generator(chat_model, message_list, json.dumps(mcp_servers_config))
            return NodeResult(
                {'result': r, 'chat_model': chat_model, 'message_list': message_list,
                 'history_message': history_message, 'question': question.content}, {},
                _write_context=write_context_stream)

        return None

    @staticmethod
    def get_history_message(history_chat_record, dialogue_number, dialogue_type, runtime_node_id):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            get_message(history_chat_record[index], dialogue_type, runtime_node_id)
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        for message in history_message:
            if isinstance(message.content, str):
                message.content = re.sub('<form_rander>[\d\D]*?<\/form_rander>', '', message.content)
        return history_message

    def generate_prompt_question(self, prompt):
        return HumanMessage(self.workflow_manage.generate_prompt(prompt))

    def generate_message_list(self, system: str, prompt: str, history_message):
        if system is not None and len(system) > 0:
            return [SystemMessage(self.workflow_manage.generate_prompt(system)), *history_message,
                    HumanMessage(self.workflow_manage.generate_prompt(prompt))]
        else:
            return [*history_message, HumanMessage(self.workflow_manage.generate_prompt(prompt))]

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else 'ai', 'content': message.content} for
                  message
                  in
                  message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result

    def get_details(self, index: int, **kwargs):
        # 删除临时生成的MCP代码文件
        if self.context.get('tool_ids'):
            executor = ToolExecutor()
            # 清理工具代码文件，延时删除，避免文件被占用
            for tool_id in self.context.get('tool_ids'):
                code_path = f'{executor.sandbox_path}/execute/{tool_id}.py'
                if os.path.exists(code_path):
                    os.remove(code_path)
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'system': self.context.get('system'),
            'history_message': [{'content': message.content, 'role': message.type} for message in
                                (self.context.get('history_message') if self.context.get(
                                    'history_message') is not None else [])],
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'reasoning_content': self.context.get('reasoning_content'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message
        }
