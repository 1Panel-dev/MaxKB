# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： ai_chat_node.py
    @date：2026/7/1 16:59
    @desc:
"""
import base64
import json
import re
from functools import reduce

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from rest_framework import serializers

from application.flow.tools import get_tools, mcp_response_generator
from application.models import Application, ApplicationAccessToken, ApplicationApiKey
from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.status import Status
from application.workflow.tools import Reasoning
from common.exception.app_exception import AppApiException
from common.utils.common import guess_image_format
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.shared_resource_auth import filter_authorized_ids
from common.utils.tool_code import ToolExecutor
from knowledge.models import File
from models_provider.models import Model
from models_provider.tools import get_model_credential, get_model_instance_by_model_workspace_id
from tools.models import Tool, ToolType


class ChatNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                               label=_("Reference Field"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))
    is_result = serializers.BooleanField(required=False, label=_('Whether to return content'))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))
    model_setting = serializers.DictField(required=False, label='Model settings')
    dialogue_type = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                          label=_("Context Type"))
    mcp_servers = serializers.JSONField(required=False, label=_("MCP Server"))
    mcp_tool_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("MCP Tool ID"))
    mcp_tool_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                         label=_("MCP Tool IDs"), )
    mcp_source = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("MCP Source"))
    tool_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                     label=_("Tool IDs"), )
    application_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                            label=_("App IDs"), )
    skill_tool_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                           label=_("Skill IDs"), )
    mcp_output_enable = serializers.BooleanField(required=False, default=True, label=_("Whether to enable MCP output"))
    video_list = serializers.ListField(required=False, label=_("video"))
    image_list = serializers.ListField(required=False, label=_("picture"))
    vision = serializers.BooleanField(required=False, default=False, label=_("vision"))


def _get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
    return model_params_setting


def _get_node_message(chat_record, runtime_node_id):
    node_details = chat_record.get_node_details_runtime_node_id(runtime_node_id)
    if node_details is None:
        return []
    return [HumanMessage(node_details.get("question")), AIMessage(node_details.get("answer"))]


def _get_workflow_message(chat_record):
    return [chat_record.get_human_message(), chat_record.get_ai_message()]


def _get_message(chat_record, dialogue_type, runtime_node_id):
    if dialogue_type == "NODE":
        return _get_node_message(chat_record, runtime_node_id)
    return _get_workflow_message(chat_record)


def _get_history_message(history_chat_record, dialogue_number, dialogue_type, runtime_node_id):
    start_index = len(history_chat_record) - dialogue_number
    history_message = reduce(
        lambda x, y: [*x, *y],
        [
            _get_message(history_chat_record[index], dialogue_type, runtime_node_id)
            for index in range(max(start_index, 0), len(history_chat_record))
        ],
        [],
    )
    for message in history_message:
        if isinstance(message.content, str):
            message.content = re.sub(r"<form_rander>.*?<\/form_rander>", "", message.content, flags=re.DOTALL)
    return history_message


def _process_images(image):
    images = []
    if isinstance(image, str) and image.startswith("http"):
        images.append({"type": "image_url", "image_url": {"url": image}})
    elif image is not None and len(image) > 0:
        for img in image:
            if "file_id" in img:
                file_id = img["file_id"]
                file = QuerySet(File).filter(id=file_id).first()
                image_bytes = file.get_bytes()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                image_format = guess_image_format(image_bytes)
                images.append(
                    {"type": "image_url", "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"}}
                )
            elif "url" in img and img["url"].startswith("http"):
                images.append({"type": "image_url", "image_url": {"url": img["url"]}})
    return images


def _process_videos(video, video_model):
    videos = []
    if isinstance(video, str) and video.startswith("http"):
        videos.append({"type": "video_url", "video_url": {"url": video}})
    elif video is not None and len(video) > 0:
        for v in video:
            if "file_id" in v:
                file_id = v["file_id"]
                file = QuerySet(File).filter(id=file_id).first()
                url = video_model.upload_file_and_get_url(file.get_bytes(), file.file_name)
                videos.append({"type": "video_url", "video_url": {"url": url}})
            elif "url" in v and v["url"].startswith("http"):
                videos.append({"type": "video_url", "video_url": {"url": v["url"]}})
    return videos


class AIChatNode(INode):
    serializer_class = ChatNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'ai-chat-node'

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        node_params = self.get_parameters()
        reasoning_content_id = str(uuid.uuid7())
        text_content_id = str(uuid.uuid7())

        model_id = node_params.get('model_id')
        model_id_type = node_params.get('model_id_type', 'custom')
        model_id_reference = node_params.get('model_id_reference')
        model_params_setting = node_params.get('model_params_setting')
        model_setting = node_params.get('model_setting')
        system = node_params.get('system', '')
        prompt = node_params.get('prompt', '')
        dialogue_number = node_params.get('dialogue_number', 0)
        dialogue_type = node_params.get('dialogue_type', 'WORKFLOW') or 'WORKFLOW'
        is_result = node_params.get('is_result', False)
        vision = node_params.get('vision', False)
        image_list = node_params.get('image_list')
        video_list = node_params.get('video_list')
        stream = node_params.get('stream', True)

        mcp_servers = node_params.get('mcp_servers')
        mcp_tool_id = node_params.get('mcp_tool_id')
        mcp_tool_ids = node_params.get('mcp_tool_ids')
        mcp_source = node_params.get('mcp_source')
        tool_ids = node_params.get('tool_ids')
        application_ids = node_params.get('application_ids')
        skill_tool_ids = node_params.get('skill_tool_ids')
        mcp_output_enable = node_params.get('mcp_output_enable', True)

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
            chat_id = None
            workspace_id = workflow_params.get('workspace_id')
        else:
            history_chat_record = workflow_params.get('history_chat_record', [])
            chat_id = workflow_params.get('chat_id')
            workspace_id = workflow_params.get('workspace_id')

        if model_id_type == 'reference' and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0], model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get('model_id', model_id)
                model_params_setting = reference_data.get('model_params_setting')

        if not model_id:
            raise Exception(_("Model is not allowed to be empty"))

        if model_params_setting is None and model_id:
            model_params_setting = _get_default_model_params_setting(model_id)

        if model_setting is None:
            model_setting = {
                'reasoning_content_enable': False,
                'reasoning_content_end': '</think>',
                'reasoning_content_start': '<think>',
            }
        self.write_context('model_setting', model_setting)

        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id, **(model_params_setting or {}))

        history_message = _get_history_message(history_chat_record, dialogue_number, dialogue_type, self.get_node_id())
        self.write_context('history_message', [
            {'content': message.content, 'role': message.type}
            for message in (history_message or [])
        ])

        question = self._generate_prompt_question(prompt, chat_model, vision, image_list, video_list)
        self.write_context('question', question.content)

        system = self.workflow_manage.generate_prompt(system)
        self.write_context('system', system)

        message_list = [*history_message, question]
        self.write_context('message_list', message_list)

        all_tool_ids = list(set(
            (mcp_tool_ids or [])
            + (tool_ids or [])
            + (skill_tool_ids or [])
            + ([mcp_tool_id] if mcp_tool_id else [])
        ))
        authorized_set = set(filter_authorized_ids('tool', all_tool_ids, workspace_id))
        mcp_tool_ids = [i for i in (mcp_tool_ids or []) if i in authorized_set]
        tool_ids = [i for i in (tool_ids or []) if i in authorized_set]
        skill_tool_ids = [i for i in (skill_tool_ids or []) if i in authorized_set]
        mcp_tool_id = mcp_tool_id if (mcp_tool_id and mcp_tool_id in authorized_set) else None

        mcp_handled = self._handle_mcp(
            mcp_source, mcp_servers, mcp_tool_id, mcp_tool_ids,
            tool_ids, application_ids, skill_tool_ids, mcp_output_enable,
            chat_model, SystemMessage(system), message_list, history_message,
            question, chat_id, workspace_id, workflow_type, reasoning_content_id, text_content_id, is_result,
        )
        if not mcp_handled:
            message_list_with_system = [SystemMessage(system)] + message_list

            if stream:
                r = chat_model.stream(message_list_with_system)
                self._stream_response(r, chat_model, message_list_with_system, question.content,
                                      reasoning_content_id, text_content_id)
            else:
                r = chat_model.invoke(message_list_with_system)
                self._invoke_response(r, chat_model, message_list_with_system, question.content, is_result, text_content_id)

    def _generate_prompt_question(self, prompt, model, vision, image_list, video_list):
        images = []
        videos = []
        if vision:
            if image_list:
                image = self.workflow_manage.get_reference_field(image_list[0], image_list[1:])
                images = _process_images(image)
            if video_list:
                video = self.workflow_manage.get_reference_field(video_list[0], video_list[1:])
                videos = _process_videos(video, model)
        return HumanMessage(
            content=[*videos, *images, {"type": "text", "text": self.workflow_manage.generate_prompt(prompt)}]
        )

    def _stream_response(self, response, chat_model, message_list, question,
                         reasoning_content_id, text_content_id):
        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.RUNNING)
        model_setting = self.get_context('model_setting') or {}
        reasoning = Reasoning(
            model_setting.get('reasoning_content_start', '<think>'),
            model_setting.get('reasoning_content_end', '</think>'),
        )
        answer = ''
        reasoning_content = ''
        response_reasoning_content = False

        for chunk in response:
            self._check_cancelled()
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
            reasoning_end = False
            if content_chunk:
                if not reasoning_end:
                    self.write(
                        ReasoningContent(reasoning_content_id, '', Status.SUCCESS, node_info,
                                         Position(self.get_node_id())))
                self.write(TextContent(text_content_id, content_chunk, Status.RUNNING, node_info,
                                       Position(self.get_node_id())))
            if reasoning_content_chunk and model_setting.get('reasoning_content_enable', False):
                self.write(ReasoningContent(reasoning_content_id, reasoning_content_chunk, Status.RUNNING, node_info,
                                            Position(self.get_node_id())))

        reasoning_end = reasoning.get_end_reasoning_content()
        answer += reasoning_end.get('content')
        reasoning_content_chunk = ''
        if not response_reasoning_content:
            reasoning_content_chunk = reasoning_end.get('reasoning_content')
        if reasoning_end.get('content'):
            self.write(TextContent(text_content_id, reasoning_end.get('content'), Status.RUNNING, node_info,
                                   Position(self.get_node_id())))
        if reasoning_content_chunk and model_setting.get('reasoning_content_enable', False):
            self.write(ReasoningContent(reasoning_content_id, reasoning_content_chunk, Status.RUNNING, node_info,
                                        Position(self.get_node_id())))

        self._write_final_context(chat_model, message_list, question, answer, reasoning_content)

    def _invoke_response(self, response, chat_model, message_list, question, is_result=False, text_content_id=None):
        model_setting = self.get_context('model_setting') or {}
        reasoning = Reasoning(
            model_setting.get('reasoning_content_start', '<think>'),
            model_setting.get('reasoning_content_end', '</think>'),
        )
        reasoning_result = reasoning.get_reasoning_content(response)
        reasoning_result_end = reasoning.get_end_reasoning_content()
        content = reasoning_result.get('content') + reasoning_result_end.get('content')
        meta = {**response.response_metadata, **response.additional_kwargs}
        if 'reasoning_content' in meta:
            reasoning_content = meta.get('reasoning_content', '') or ''
        else:
            reasoning_content = (reasoning_result.get('reasoning_content') or '') + (
                    reasoning_result_end.get('reasoning_content') or ''
            )
        self._write_final_context(chat_model, message_list, question, content, reasoning_content)
        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(text_content_id, content, Status.SUCCESS, node_info, Position(self.get_node_id())))

    def _write_final_context(self, chat_model, message_list, question, answer, reasoning_content):
        message_tokens = chat_model.get_num_tokens_from_messages(message_list)
        answer_tokens = chat_model.get_num_tokens(answer)
        self.write_context('message_tokens', message_tokens)
        self.write_context('answer_tokens', answer_tokens)
        self.write_context('answer', answer)
        self.write_context('question', question)
        self.write_context('reasoning_content', reasoning_content)

    def _handle_mcp(
            self, mcp_source, mcp_servers, mcp_tool_id, mcp_tool_ids,
            tool_ids, application_ids, skill_tool_ids, mcp_output_enable,
            chat_model, system_prompt, message_list, history_message,
            question, chat_id, workspace_id, workflow_type,
            reasoning_content_id, text_content_id, is_result=False,
    ):
        mcp_servers_config = {}

        if mcp_source is None:
            mcp_source = 'custom'
        if not mcp_tool_ids:
            mcp_tool_ids = []
        if mcp_tool_id:
            mcp_tool_ids = list(set(mcp_tool_ids + [mcp_tool_id]))

        if mcp_source == 'custom' and mcp_servers:
            mcp_servers_config = json.loads(mcp_servers)
            mcp_servers_config = self._handle_variables(mcp_servers_config)
        elif mcp_tool_ids:
            mcp_tools = QuerySet(Tool).filter(id__in=mcp_tool_ids).values()
            for mcp_tool in mcp_tools:
                if mcp_tool and mcp_tool['is_active']:
                    mcp_servers_config = {**mcp_servers_config, **json.loads(mcp_tool['code'])}
                    mcp_servers_config = self._handle_variables(mcp_servers_config)

        ToolExecutor().validate_mcp_transport(json.dumps(mcp_servers_config))

        tool_init_params = {}
        if workflow_type == WorkflowType.KNOWLEDGE:
            source_id = self.get_workflow_parameters().get('knowledge_id')
            source_type = 'KNOWLEDGE'
        elif workflow_type == WorkflowType.TOOL:
            source_id = self.get_workflow_parameters().get('tool_id')
            source_type = 'TOOL'
        else:
            source_id = self.get_workflow_parameters().get('application_id')
            source_type = 'APPLICATION'

        tools = get_tools(source_type, chat_id, tool_ids, workspace_id)
        if tool_ids and len(tool_ids) > 0:
            self.write_context('tool_ids', tool_ids)
            custom_tools_map = {
                str(t.id): t for t in QuerySet(Tool).filter(id__in=tool_ids, tool_type=ToolType.CUSTOM, is_active=True)
            }
            for tool_id in tool_ids:
                tool = custom_tools_map.get(str(tool_id))
                if tool is None:
                    continue
                executor = ToolExecutor()
                init_params_default_value = {i['field']: i.get('default_value') for i in tool.init_field_list}
                if tool.init_params is not None:
                    tool_init_params = init_params_default_value | json.loads(rsa_long_decrypt(tool.init_params))
                else:
                    tool_init_params = init_params_default_value
                tool_config = executor.get_tool_mcp_config(tool, tool_init_params)
                mcp_servers_config[str(tool.id)] = tool_config

        if application_ids and len(application_ids) > 0:
            self.write_context('application_ids', application_ids)
            apps_map = {str(a.id): a for a in QuerySet(Application).filter(id__in=application_ids, is_publish=True)}
            app_keys_map = {
                str(ak.application_id): ak
                for ak in QuerySet(ApplicationApiKey).filter(application_id__in=application_ids, is_active=True)
            }
            app_access_tokens_map = {
                str(at.application_id): at
                for at in QuerySet(ApplicationAccessToken).filter(application_id__in=application_ids)
            }
            for application_id in application_ids:
                app = apps_map.get(str(application_id))
                if app is None:
                    continue
                app_key = app_keys_map.get(str(application_id))
                if app_key is not None:
                    api_key = app_key.secret_key
                    application_access_token = app_access_tokens_map.get(str(app_key.application_id))
                    if application_access_token is not None and application_access_token.authentication:
                        raise AppApiException(
                            500,
                            _("Agent 【{name}】 access token authentication is not supported for agent tool").format(
                                name=app.name
                            ),
                        )
                else:
                    raise AppApiException(
                        500, _("Agent Key is required for agent tool 【{name}】").format(name=app.name)
                    )
                executor = ToolExecutor()
                app_config = executor.get_app_mcp_config(api_key)
                mcp_servers_config[app.name] = app_config

        if skill_tool_ids and len(skill_tool_ids) > 0:
            self.write_context('skill_tool_ids', skill_tool_ids)
            skill_file_items = []
            skill_tools_map = {str(t.id): t for t in QuerySet(Tool).filter(id__in=skill_tool_ids, is_active=True)}
            for tool_id in skill_tool_ids:
                tool = skill_tools_map.get(str(tool_id))
                if tool is None:
                    continue
                init_params_default_value = {i['field']: i.get('default_value') for i in tool.init_field_list}
                if tool.init_params is not None:
                    params = init_params_default_value | json.loads(rsa_long_decrypt(tool.init_params))
                else:
                    params = init_params_default_value
                skill_file_items.append({'tool_id': str(tool.id), 'file_id': tool.code, 'params': params})
            mcp_servers_config['skills'] = skill_file_items

        if len(mcp_servers_config) > 0 or len(tools) > 0:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.RUNNING)
            tool_content_id = str(uuid.uuid7())
            r = mcp_response_generator(
                chat_model, system_prompt, message_list,
                json.dumps(mcp_servers_config), mcp_output_enable,
                tool_init_params, source_id, source_type,
                chat_id, tools,
            )
            answer = ''
            tool_calls_map = {}
            for chunk in r:
                self._check_cancelled()
                if isinstance(chunk, ToolMessage):
                    tool_call = tool_calls_map.get(chunk.tool_call_id, {})
                    self.write(ToolContent(
                        tool_content_id,
                        tool_call.get('name', getattr(chunk, 'name', '')),
                        json.dumps(tool_call.get('args', {}), ensure_ascii=False),
                        chunk.content,
                        Status.RUNNING,
                        node_info,
                        Position(self.get_node_id())
                    ))
                    continue

                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        tool_calls_map[tool_call.get('id', '')] = tool_call

                answer += chunk.content if hasattr(chunk, 'content') else str(chunk)
                if chunk.content:
                    self.write(TextContent(text_content_id, chunk.content, Status.RUNNING, node_info,
                                           Position(self.get_node_id())))
            self._write_final_context(chat_model, message_list, question.content, answer, '')
            return True

        return False

    def _handle_variables(self, tool_params):
        for k, v in tool_params.items():
            if isinstance(v, str):
                tool_params[k] = self.workflow_manage.generate_prompt(v)
            elif isinstance(v, dict):
                self._handle_variables(v)
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                tool_params[k] = self._get_reference_content(v)
        return tool_params

    def _get_reference_content(self, fields):
        if fields:
            return str(self.workflow_manage.get_reference_field(fields[0], fields[1:]))
        return ''
