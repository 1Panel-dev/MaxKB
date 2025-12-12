# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： utils.py
    @date：2024/6/6 15:15
    @desc:
"""
import asyncio
import json
import queue
import threading
from typing import Iterator

from django.http import StreamingHttpResponse
from langchain_core.messages import BaseMessageChunk, BaseMessage, ToolMessage, AIMessageChunk
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from application.flow.i_step_node import WorkFlowPostHandler
from common.result import result
from common.utils.logger import maxkb_logger


class Reasoning:
    def __init__(self, reasoning_content_start, reasoning_content_end):
        self.content = ""
        self.reasoning_content = ""
        self.all_content = ""
        self.reasoning_content_start_tag = reasoning_content_start
        self.reasoning_content_end_tag = reasoning_content_end
        self.reasoning_content_start_tag_len = len(
            reasoning_content_start) if reasoning_content_start is not None else 0
        self.reasoning_content_end_tag_len = len(reasoning_content_end) if reasoning_content_end is not None else 0
        self.reasoning_content_end_tag_prefix = reasoning_content_end[
            0] if self.reasoning_content_end_tag_len > 0 else ''
        self.reasoning_content_is_start = False
        self.reasoning_content_is_end = False
        self.reasoning_content_chunk = ""

    def get_end_reasoning_content(self):
        if not self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': self.all_content, 'reasoning_content': ''}
            self.reasoning_content_chunk = ""
            return r
        if self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
            self.reasoning_content_chunk = ""
            return r
        return {'content': '', 'reasoning_content': ''}

    def _normalize_content(self, content):
        """将不同类型的内容统一转换为字符串"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 处理包含多种内容类型的列表
            normalized_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        normalized_parts.append(item.get('text', ''))
            return ''.join(normalized_parts)
        else:
            return str(content)

    def get_reasoning_content(self, chunk):
        # 如果没有开始思考过程标签那么就全是结果
        if self.reasoning_content_start_tag is None or len(self.reasoning_content_start_tag) == 0:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 如果没有结束思考过程标签那么就全部是思考过程
        if self.reasoning_content_end_tag is None or len(self.reasoning_content_end_tag) == 0:
            return {'content': '', 'reasoning_content': chunk.content}
        chunk.content = self._normalize_content(chunk.content)
        self.all_content += chunk.content
        if not self.reasoning_content_is_start and len(self.all_content) >= self.reasoning_content_start_tag_len:
            if self.all_content.startswith(self.reasoning_content_start_tag):
                self.reasoning_content_is_start = True
                self.reasoning_content_chunk = self.all_content[self.reasoning_content_start_tag_len:]
            else:
                if not self.reasoning_content_is_end:
                    self.reasoning_content_is_end = True
                    self.content += self.all_content
                    return {'content': self.all_content,
                            'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                             '') if chunk.additional_kwargs else ''
                            }
        else:
            if self.reasoning_content_is_start:
                self.reasoning_content_chunk += chunk.content
        reasoning_content_end_tag_prefix_index = self.reasoning_content_chunk.find(
            self.reasoning_content_end_tag_prefix)
        if self.reasoning_content_is_end:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                                               '') if chunk.additional_kwargs else ''
                    }
        # 是否包含结束
        if reasoning_content_end_tag_prefix_index > -1:
            if len(self.reasoning_content_chunk) - reasoning_content_end_tag_prefix_index >= self.reasoning_content_end_tag_len:
                reasoning_content_end_tag_index = self.reasoning_content_chunk.find(self.reasoning_content_end_tag)
                if reasoning_content_end_tag_index > -1:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_index]
                    content_chunk = self.reasoning_content_chunk[
                                    reasoning_content_end_tag_index + self.reasoning_content_end_tag_len:]
                    self.reasoning_content += reasoning_content_chunk
                    self.content += content_chunk
                    self.reasoning_content_chunk = ""
                    self.reasoning_content_is_end = True
                    return {'content': content_chunk, 'reasoning_content': reasoning_content_chunk}
                else:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_prefix_index + 1]
                    self.reasoning_content_chunk = self.reasoning_content_chunk.replace(reasoning_content_chunk, '')
                    self.reasoning_content += reasoning_content_chunk
                    return {'content': '', 'reasoning_content': reasoning_content_chunk}
            else:
                return {'content': '', 'reasoning_content': ''}

        else:
            if self.reasoning_content_is_end:
                self.content += chunk.content
                return {'content': chunk.content, 'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                                                   '') if chunk.additional_kwargs else ''
                        }
            else:
                # aaa
                result = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
                self.reasoning_content += self.reasoning_content_chunk
                self.reasoning_content_chunk = ""
                return result


def event_content(chat_id, chat_record_id, response, workflow,
                  write_context,
                  post_handler: WorkFlowPostHandler):
    """
    用于处理流式输出
    @param chat_id:         会话id
    @param chat_record_id:  对话记录id
    @param response:        响应数据
    @param workflow:        工作流管理器
    @param write_context    写入节点上下文
    @param post_handler:    后置处理器
    """
    answer = ''
    try:
        for chunk in response:
            answer += chunk.content
            yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                         'content': chunk.content, 'is_end': False}, ensure_ascii=False) + "\n\n"
        write_context(answer, 200)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '', 'is_end': True}, ensure_ascii=False) + "\n\n"
    except Exception as e:
        answer = str(e)
        write_context(answer, 500)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': answer, 'is_end': True}, ensure_ascii=False) + "\n\n"


def to_stream_response(chat_id, chat_record_id, response: Iterator[BaseMessageChunk], workflow, write_context,
                       post_handler):
    """
    将结果转换为服务流输出
    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    r = StreamingHttpResponse(
        streaming_content=event_content(chat_id, chat_record_id, response, workflow, write_context, post_handler),
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r


def to_response(chat_id, chat_record_id, response: BaseMessage, workflow, write_context,
                post_handler: WorkFlowPostHandler):
    """
    将结果转换为服务输出

    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    answer = response.content
    write_context(answer)
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})


def to_response_simple(chat_id, chat_record_id, response: BaseMessage, workflow,
                       post_handler: WorkFlowPostHandler):
    answer = response.content
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})


def to_stream_response_simple(stream_event):
    r = StreamingHttpResponse(
        streaming_content=stream_event,
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r


tool_message_json_template = """
```json
%s
```
"""

tool_message_complete_template = """
<details>
    <summary>
        <strong>Called MCP Tool: <em>%s</em></strong>
    </summary>

**Input:**
%s

**Output:**
%s

</details>

"""


def generate_tool_message_complete(name, input_content, output_content):
    """生成包含输入和输出的工具消息模版"""
    # 格式化输入
    if '```' not in input_content:
        input_formatted = tool_message_json_template % input_content
    else:
        input_formatted = input_content

    # 格式化输出
    if '```' not in output_content:
        output_formatted = tool_message_json_template % output_content
    else:
        output_formatted = output_content

    return tool_message_complete_template % (name, input_formatted, output_formatted)


# 全局单例事件循环
_global_loop = None
_loop_thread = None
_loop_lock = threading.Lock()


def get_global_loop():
    """获取全局共享的事件循环"""
    global _global_loop, _loop_thread

    with _loop_lock:
        if _global_loop is None:
            _global_loop = asyncio.new_event_loop()

            def run_forever():
                asyncio.set_event_loop(_global_loop)
                _global_loop.run_forever()

            _loop_thread = threading.Thread(target=run_forever, daemon=True, name="GlobalAsyncLoop")
            _loop_thread.start()

    return _global_loop


async def _yield_mcp_response(chat_model, message_list, mcp_servers, mcp_output_enable=True):
    try:
        client = MultiServerMCPClient(json.loads(mcp_servers))
        tools = await client.get_tools()
        agent = create_react_agent(chat_model, tools)
        response = agent.astream({"messages": message_list}, stream_mode='messages')

        # 用于存储工具调用信息（按 tool_id）以及按 index 聚合分片
        tool_calls_info = {}
        _tool_fragments = {}  # index -> {'id':..., 'name':..., 'arguments':...}

        async for chunk in response:
            if isinstance(chunk[0], AIMessageChunk):
                tool_calls = chunk[0].additional_kwargs.get('tool_calls', [])
                for tool_call in tool_calls:
                    idx = tool_call.get('index')
                    if idx is None:
                        continue
                    entry = _tool_fragments.setdefault(idx, {'id': '', 'name': '', 'arguments': ''})

                    # 更新 id 与 name（如果有）
                    if tool_call.get('id'):
                        entry['id'] = tool_call.get('id')

                    func = tool_call.get('function', {})
                    # arguments 可能在 function.arguments 或顶层 arguments
                    part_args = ''
                    if isinstance(func, dict) and 'arguments' in func:
                        part_args = func.get('arguments') or ''
                        if func.get('name'):
                            entry['name'] = func.get('name')
                    else:
                        part_args = tool_call.get('arguments', '') or ''

                    # 统一为字符串
                    if not isinstance(part_args, str):
                        try:
                            part_args = json.dumps(part_args, ensure_ascii=False)
                        except Exception:
                            part_args = str(part_args)

                    entry['arguments'] += part_args

                    # 尝试判断 JSON 是否完整（若 arguments 是 JSON），完整则提交到 tool_calls_info
                    try:
                        json.loads(entry['arguments'])
                        if entry['id']:
                            tool_calls_info[entry['id']] = {
                                'name': entry.get('name', ''),
                                'input': entry['arguments']
                            }
                            _tool_fragments.pop(idx, None)
                    except Exception:
                        # 如果不是完整 JSON，继续等待后续片段
                        pass

                yield chunk[0]

            if mcp_output_enable and isinstance(chunk[0], ToolMessage):
                tool_id = chunk[0].tool_call_id
                if tool_id in tool_calls_info:
                    tool_info = tool_calls_info[tool_id]
                    content = generate_tool_message_complete(
                        tool_info['name'],
                        tool_info['input'],
                        chunk[0].content
                    )
                    chunk[0].content = content
                yield chunk[0]

    except ExceptionGroup as eg:

        def get_real_error(exc):
            if isinstance(exc, ExceptionGroup):
                return get_real_error(exc.exceptions[0])
            return exc

        real_error = get_real_error(eg)
        error_msg = f"{type(real_error).__name__}: {str(real_error)}"
        raise RuntimeError(error_msg) from None

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        raise RuntimeError(error_msg) from None



def mcp_response_generator(chat_model, message_list, mcp_servers, mcp_output_enable=True):
    """使用全局事件循环，不创建新实例"""
    result_queue = queue.Queue()
    loop = get_global_loop()  # 使用共享循环

    async def _run():
        try:
            async_gen = _yield_mcp_response(chat_model, message_list, mcp_servers, mcp_output_enable)
            async for chunk in async_gen:
                result_queue.put(('data', chunk))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            result_queue.put(('error', e))
        finally:
            result_queue.put(('done', None))

    # 在全局循环中调度任务
    asyncio.run_coroutine_threadsafe(_run(), loop)

    while True:
        msg_type, data = result_queue.get()
        if msg_type == 'done':
            break
        if msg_type == 'error':
            raise data
        yield data


async def anext_async(agen):
    return await agen.__anext__()
