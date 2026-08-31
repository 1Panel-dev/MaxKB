# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： chat.py
@date：2025/6/9 11:23
@desc:
"""

import json
import os
import queue as thread_queue
import threading
from gettext import gettext
from typing import List, Dict

import uuid_utils
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rest_framework import serializers
from rest_framework.request import Request

from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import (
    BaseGenerateHumanMessageStep,
)
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.flow.common import Answer
from application.flow.tools import to_stream_response_simple
from application.models import (
    Application,
    ApplicationTypeChoices,
    ChatUserType,
    ApplicationChatUserStats,
    ApplicationAccessToken,
    ChatRecord,
    Chat,
    ApplicationVersion,
)
from application.serializers.application import ApplicationOperateSerializer
from application.serializers.common import ChatInfo
from application.workflow.common import WorkflowType, new_instance
from application.workflow.message.aggregator import AggregationManager
from application.workflow.message.struct.failure_content import FailureContent
from application.workflow.message.struct.form_content import FormContent
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.message_queue import get_message_queue
from application.workflow.nodes import get_start_node
from application.workflow.workflow_manage import WorkflowManage, CallBack
from application.workflow.workflow_run_registry import WorkflowRunRegistry
from common import result
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException, AppChatNumOutOfBoundsFailed, ChatException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import flat_map, get_file_content, is_valid_uuid
from common.utils.logger import maxkb_logger
from knowledge.models import Document, Paragraph
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model, Status
from models_provider.tools import get_model_instance_by_model_workspace_id
from system_manage.models.chat_user_token_quota import ChatUserTokenQuota
from system_manage.models.resource_mapping import ResourceMapping


class ChatMessagesSerializers(serializers.Serializer):
    role = serializers.CharField(required=True, label=_("Role"))
    content = serializers.CharField(required=True, label=_("Content"))


class GeneratePromptSerializers(serializers.Serializer):
    prompt = serializers.CharField(required=True, label=_("Prompt template"))
    messages = serializers.ListSerializer(child=ChatMessagesSerializers(), required=True, label=_("Chat context"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        messages = self.data.get("messages")

        if len(messages) > 30:
            raise AppApiException(400, _("Too many messages"))

        for index in range(len(messages)):
            role = messages[index].get("role")
            if role == "ai" and index % 2 != 1:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role == "user" and index % 2 != 0:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role not in ["user", "ai"]:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))


class ChatMessageSerializers(serializers.Serializer):
    message = serializers.DictField(required=True, label=_("User Questions"))
    stream = serializers.BooleanField(required=True, label=_("Is the answer in streaming mode"))
    re_chat = serializers.BooleanField(required=True, label=_("Do you want to reply again"))
    chat_record_id = serializers.UUIDField(required=False, allow_null=True, label=_("Conversation record id"))

    node_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Node id"))

    runtime_node_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, label=_("Runtime node id")
    )

    node_data = serializers.DictField(required=False, allow_null=True, label=_("Node parameters"))

    form_data = serializers.DictField(required=False, label=_("Global variables"))
    child_node = serializers.DictField(required=False, allow_null=True, label=_("Child Nodes"))


def get_post_handler(chat_info: ChatInfo):
    class PostHandler(PostResponseHandler):
        def handler(
            self,
            chat_id,
            chat_record_id,
            paragraph_list: List[Paragraph],
            problem_text: str,
            answer_text,
            manage: PipelineManage,
            step: BaseChatStep,
            padding_problem_text: str = None,
            **kwargs,
        ):
            answer_list = [
                [
                    Answer(
                        answer_text,
                        "ai-chat-node",
                        "ai-chat-node",
                        "ai-chat-node",
                        {},
                        "ai-chat-node",
                        kwargs.get("reasoning_content", ""),
                    ).to_dict()
                ]
            ]
            chat_record = ChatRecord(
                id=chat_record_id,
                chat_id=chat_id,
                problem_text=problem_text,
                answer_text=answer_text,
                details=manage.get_details(),
                message_tokens=manage.context["message_tokens"],
                answer_tokens=manage.context["answer_tokens"],
                answer_text_list=answer_list,
                run_time=manage.context["run_time"],
                index=len(chat_info.chat_record_list) + 1,
                ip_address=chat_info.ip_address,
                source=chat_info.source,
            )
            chat_info.append_chat_record(chat_record)
            # 重新设置缓存
            chat_info.set_cache()

    return PostHandler()


class DebugChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    # 以下字段用于「缓存缺失时按前端提供的 chat_id 现开会话」（open-if-missing）
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=False, allow_null=True, label=_("Application ID"))
    chat_user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Client Type"))
    ip_address = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("IP Address"))
    source = serializers.JSONField(required=False, allow_null=True, label=_("Source"))

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get("chat_id")
        chat_info: ChatInfo = ChatInfo.get_cache(chat_id)
        if chat_info is None:
            # 前端本地生成的 chat_id 首次发消息时，缓存里还没有会话，按该 id 现开一个 debug 会话。
            OpenChatSerializers(
                data={
                    "workspace_id": self.data.get("workspace_id"),
                    "application_id": self.data.get("application_id"),
                    "chat_user_id": self.data.get("chat_user_id"),
                    "chat_user_type": self.data.get("chat_user_type"),
                    "ip_address": self.data.get("ip_address"),
                    "source": self.data.get("source"),
                    "debug": True,
                }
            ).open(chat_id=str(chat_id))
            chat_info = ChatInfo.get_cache(chat_id)
        application = QuerySet(Application).filter(id=chat_info.application_id).first()
        chat_info.application = application
        return ChatSerializers(
            data={
                "chat_id": chat_id,
                "chat_user_id": chat_info.chat_user_id,
                "chat_user_type": chat_info.chat_user_type,
                "application_id": chat_info.application.id,
                "debug": True,
            }
        ).chat(instance, base_to_response)


SYSTEM_ROLE = get_file_content(os.path.join(PROJECT_DIR, "apps", "chat", "template", "generate_prompt_system"))


class PromptGenerateSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_("Workspace ID"))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model"))
    application_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Application"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        query_set = QuerySet(Application).filter(id=self.data.get("application_id"))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        application = query_set.first()
        if application is None:
            raise AppApiException(500, _("Application id does not exist"))
        return application

    def generate_prompt(self, instance: dict):
        application = self.is_valid(raise_exception=True)
        GeneratePromptSerializers(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        model_id = self.data.get("model_id")
        prompt = instance.get("prompt")
        messages = instance.get("messages")

        message = messages[-1]["content"]
        q = prompt.replace("{userInput}", message)

        messages[-1]["content"] = q
        SUPPORTED_MODEL_TYPES = ["LLM", "IMAGE"]
        model_exist = QuerySet(Model).filter(id=model_id, model_type__in=SUPPORTED_MODEL_TYPES).exists()
        if not model_exist:
            raise Exception(_("Model does not exists or is not an LLM model"))

        def process():
            model = get_model_instance_by_model_workspace_id(
                model_id=model_id, workspace_id=workspace_id, **application.model_params_setting
            )
            try:
                for r in model.stream(
                    [
                        SystemMessage(content=SYSTEM_ROLE),
                        *[
                            HumanMessage(content=m.get("content"))
                            if m.get("role") == "user"
                            else AIMessage(content=m.get("content"))
                            for m in messages
                        ],
                    ]
                ):
                    yield "data: " + json.dumps({"content": r.content}) + "\n\n"
            except Exception as e:
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

        return to_stream_response_simple(process())


class OpenAIMessage(serializers.Serializer):
    content = serializers.CharField(required=True, label=_("content"))
    role = serializers.CharField(required=True, label=_("Role"))


class OpenAIInstanceSerializer(serializers.Serializer):
    messages = serializers.ListField(child=OpenAIMessage())
    chat_id = serializers.UUIDField(required=False, label=_("Conversation ID"))
    re_chat = serializers.BooleanField(required=False, label=_("Regenerate"))
    stream = serializers.BooleanField(required=False, label=_("Streaming Output"))


class OpenAIChatSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    ip_address = serializers.CharField(required=False, label=_("IP Address"))
    source = serializers.JSONField(required=False, label=_("Source"))

    @staticmethod
    def get_message(instance):
        return instance.get("messages")[-1].get("content")

    @staticmethod
    def generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type, ip_address, source):
        if chat_id is None:
            chat_id = str(uuid.uuid1())
            chat_info = ChatInfo(chat_id, chat_user_id, chat_user_type, ip_address, source, [], [], application_id)
            chat_info.set_cache()
        else:
            chat_info = ChatInfo.get_cache(chat_id)
            if chat_info is None:
                open_chat = ChatSerializers(
                    data={
                        "chat_id": chat_id,
                        "chat_user_id": chat_user_id,
                        "chat_user_type": chat_user_type,
                        "application_id": application_id,
                        "ip_address": ip_address,
                        "source": source,
                    }
                )
                open_chat.is_valid(raise_exception=True)
                chat_info = open_chat.re_open_chat(chat_id)
                chat_info.set_cache()
        return chat_id

    def chat(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            OpenAIInstanceSerializer(data=instance).is_valid(raise_exception=True)
        chat_id = instance.get("chat_id")
        message = self.get_message(instance)
        re_chat = instance.get("re_chat", False)
        stream = instance.get("stream", False)
        application_id = self.data.get("application_id")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        chat_id = self.generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type, ip_address, source)
        return ChatSerializers(
            data={
                "chat_id": chat_id,
                "chat_user_id": chat_user_id,
                "chat_user_type": chat_user_type,
                "application_id": application_id,
                "ip_address": ip_address,
                "source": source,
            }
        ).chat(
            {
                "message": message,
                "re_chat": re_chat,
                "stream": stream,
                "form_data": instance.get("form_data", {}),
                "image_list": instance.get("image_list", []),
                "document_list": instance.get("document_list", []),
                "audio_list": instance.get("audio_list", []),
                "other_list": instance.get("other_list", []),
            },
            base_to_response=OpenaiToResponse(),
        )


class ChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    application_id = serializers.UUIDField(required=True, allow_null=True, label=_("Application ID"))
    debug = serializers.BooleanField(required=False, label=_("Debug"))
    ip_address = serializers.CharField(required=False, label=_("IP Address"), allow_null=True, allow_blank=True)
    source = serializers.JSONField(required=False, label=_("Source"))

    def is_valid_application_workflow(self, *, raise_exception=False):
        self.is_valid_intraday_access_num()

    def is_valid_chat_id(self, chat_info: ChatInfo):
        if self.data.get("application_id") is not None and self.data.get("application_id") != str(
            chat_info.application_id
        ):
            raise ChatException(500, _("Conversation does not exist"))

    def is_valid_intraday_access_num(self):
        if not self.data.get("debug") and [
            ChatUserType.ANONYMOUS_USER.value,
            ChatUserType.CHAT_USER.value,
        ].__contains__(self.data.get("chat_user_type")):
            access_client = (
                QuerySet(ApplicationChatUserStats)
                .filter(chat_user_id=self.data.get("chat_user_id"), application_id=self.data.get("application_id"))
                .first()
            )
            if access_client is None:
                access_client = ApplicationChatUserStats(
                    chat_user_id=self.data.get("chat_user_id"),
                    chat_user_type=self.data.get("chat_user_type"),
                    application_id=self.data.get("application_id"),
                    access_num=0,
                    intraday_access_num=0,
                )
                access_client.save()

            application_access_token = (
                QuerySet(ApplicationAccessToken).filter(application_id=self.data.get("application_id")).first()
            )
            if application_access_token.access_num <= access_client.intraday_access_num:
                raise AppChatNumOutOfBoundsFailed(1002, _("The number of visits exceeds today's visits"))

    def is_valid_application_simple(self, *, chat_info: ChatInfo, raise_exception=False):
        self.is_valid_intraday_access_num()
        model_id = chat_info.application.model_id
        if model_id is None:
            return chat_info
        model = QuerySet(Model).filter(id=model_id).first()
        if model is None:
            return chat_info
        if model.status == Status.ERROR:
            raise ChatException(500, _("The current model is not available"))
        if model.status == Status.DOWNLOAD:
            raise ChatException(500, _("The model is downloading, please try again later"))
        return chat_info

    def chat_simple(self, chat_info: ChatInfo, instance, base_to_response):
        message_dict = instance.get("message")
        message = message_dict.get("content", "") if isinstance(message_dict, dict) else message_dict
        re_chat = instance.get("re_chat")
        stream = instance.get("stream")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        form_data = instance.get("form_data")
        chat_record_id = instance.get("chat_record_id")
        pipeline_manage_builder = PipelineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipeline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipeline_message = (
            pipeline_manage_builder.append_step(BaseSearchDatasetStep)
            .append_step(BaseGenerateHumanMessageStep)
            .append_step(BaseChatStep)
            .add_base_to_response(base_to_response)
            .add_debug(self.data.get("debug", False))
            .build()
        )
        exclude_paragraph_id_list = []
        # 相同问题是否需要排除已经查询到的段落
        if re_chat:
            paragraph_id_list = flat_map(
                [
                    [paragraph.get("id") for paragraph in chat_record.details["search_step"]["paragraph_list"]]
                    for chat_record in chat_info.chat_record_list
                    if chat_record.problem_text == message
                    and "search_step" in chat_record.details
                    and "paragraph_list" in chat_record.details["search_step"]
                ]
            )
            exclude_paragraph_id_list = list(set(paragraph_id_list))
        # 构建运行参数
        params = chat_info.to_pipeline_manage_params(
            message,
            get_post_handler(chat_info),
            exclude_paragraph_id_list,
            chat_user_id,
            chat_user_type,
            ip_address,
            source,
            stream,
            form_data,
        )
        if chat_record_id:
            params["chat_record_id"] = chat_record_id
        chat_info.set_chat(message)
        # 运行流水线作业
        pipeline_message.run(params)
        return pipeline_message.context["chat_result"]

    @staticmethod
    def get_chat_record(chat_info, chat_record_id):
        if chat_info is not None:
            chat_record_list = [
                chat_record for chat_record in chat_info.chat_record_list if str(chat_record.id) == str(chat_record_id)
            ]
            if chat_record_list is not None and len(chat_record_list):
                return chat_record_list[-1]
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_info.chat_id).first()
            if chat_record is None:
                if not is_valid_uuid(chat_record_id):
                    raise ChatException(500, _("Conversation record does not exist"))
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id).first()
        return chat_record

    def chat_work_flow(self, chat_info: ChatInfo, instance: dict, base_to_response):
        import queue

        message_dict = instance.get("message")
        message = message_dict.get("content", "") if isinstance(message_dict, dict) else message_dict
        re_chat = instance.get("re_chat")
        stream = instance.get("stream")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        form_data = instance.get("form_data")
        image_list = message_dict.get("image_list", []) if isinstance(message_dict, dict) else []
        video_list = message_dict.get("video_list", []) if isinstance(message_dict, dict) else []
        document_list = message_dict.get("document_list", []) if isinstance(message_dict, dict) else []
        audio_list = message_dict.get("audio_list", []) if isinstance(message_dict, dict) else []
        other_list = message_dict.get("other_list", []) if isinstance(message_dict, dict) else []
        workspace_id = chat_info.application.workspace_id
        chat_record_id = instance.get("chat_record_id")
        position = instance.get("position")
        chunk_id = instance.get("chunk_id")
        debug = self.data.get("debug", False)
        history_chat_record = chat_info.chat_record_list
        if chat_record_id is not None:
            chat_record = self.get_chat_record(chat_info, chat_record_id)
            if chat_record:
                history_chat_record = [r for r in chat_info.chat_record_list if str(r.id) != chat_record_id]

        work_flow = chat_info.application.work_flow
        workflow = new_instance(work_flow, WorkflowType.APPLICATION)

        chat_record_id_str = str(uuid.uuid7()) if chat_record_id is None else str(chat_record_id)

        parameters = {
            "history_chat_record": history_chat_record,
            "question": message,
            "chat_id": chat_info.chat_id,
            "chat_record_id": chat_record_id_str,
            "stream": stream,
            "re_chat": re_chat,
            "chat_user_id": chat_user_id,
            "chat_user_type": chat_user_type,
            "ip_address": ip_address,
            "source": source,
            "workspace_id": workspace_id,
            "debug": debug,
            "chat_user": chat_info.get_chat_user(),
            "chat_user_group": chat_info.get_chat_user_group(),
            "application_id": str(chat_info.application_id),
            "form_data": form_data or {},
            "position": position,
            "chunk_id": chunk_id,
            "image_list": image_list or [],
            "document_list": document_list or [],
            "audio_list": audio_list or [],
            "video_list": video_list or [],
            "other_list": other_list or [],
        }

        result_queue = queue.Queue()

        aggregation = AggregationManager()
        self.save_chat_record(chat_info, chat_info.chat_id, chat_record_id_str, message_dict)

        def on_next(wf_manage, content):
            aggregation.aggregate(content)
            message_queue = get_message_queue()
            message_queue.produce(chat_record_id_str, content.to_dict())
            if isinstance(content, TextContent):
                result_queue.put(
                    (
                        "chunk",
                        {
                            "content": [
                                {
                                    "id": content.id,
                                    "type": "TEXT",
                                    "content": content.content,
                                }
                            ]
                        },
                    )
                )
            elif isinstance(content, ReasoningContent):
                result_queue.put(
                    (
                        "chunk",
                        {
                            "content": [
                                {
                                    "id": content.id,
                                    "type": "REASONING",
                                    "content": content.content,
                                    "status": content.status.value if content.status else None,
                                }
                            ]
                        },
                    )
                )
            elif isinstance(content, ToolContent):
                result_queue.put(
                    (
                        "chunk",
                        {
                            "content": [
                                {
                                    "id": content.id,
                                    "type": "TOOL",
                                    "content": content.content,
                                    "arguments": content.arguments,
                                    "result": content.result,
                                    "status": content.status.value if content.status else None,
                                }
                            ]
                        },
                    )
                )
            elif isinstance(content, FormContent):

                def position_to_dict(pos):
                    if pos is None:
                        return None
                    return {"id": pos.id, "index": pos.index, "children": position_to_dict(pos.children)}

                result_queue.put(
                    (
                        "chunk",
                        {
                            "content": [
                                {
                                    "id": content.id,
                                    "type": "FORM",
                                    "form_field_list": content.form_field_list,
                                    "form_content_format": content.form_content_format,
                                    "is_submit": content.is_submit,
                                    "form_data": content.form_data,
                                    "status": content.status.value if content.status else None,
                                    "position": position_to_dict(content.position),
                                    "chat_record_id": chat_record_id_str,
                                }
                            ]
                        },
                    )
                )

        def on_complete(wf_manage, error):
            # 注销工作流实例
            WorkflowRunRegistry.unregister(chat_record_id_str, str(chat_info.chat_id))
            message_queue = get_message_queue()
            if error:
                result_queue.put(("error", error))
                message_queue.produce(
                    chat_record_id_str,
                    FailureContent(str(uuid_utils.uuid7()), str(error), Status.SUCCESS, None, None).to_dict(),
                )
            QuerySet(ChatRecord).filter(id=chat_record_id).update()
            self.update_chat_record(
                chat_info, chat_info.chat_id, chat_record_id_str, wf_manage.context, aggregation.get_contents()
            )
            result_queue.put(("done", None))
            message_queue.produce_done(chat_record_id_str)

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            return get_start_node(wf, wm, WorkflowType.APPLICATION, position)

        # 判断是否是 Form 提交（有 position 和 chat_record_id）
        if position and chat_record_id:
            # 从历史 context 恢复
            work_flow_manage = WorkflowManage.from_context(
                chat_record_id=chat_record_id,
                workflow=workflow,
                parameters=parameters,
                workflow_type=WorkflowType.APPLICATION,
                call_back=call_back,
                get_start_node=get_start_node_fn,
            )
            if work_flow_manage is None:
                # 恢复失败，回退到正常流程
                work_flow_manage = WorkflowManage(
                    workflow, parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
                )
        else:
            # 正常创建新的 WorkflowManage
            work_flow_manage = WorkflowManage(
                workflow, parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
            )

        work_flow_manage.start_node.workflow_manage = work_flow_manage

        # 注册工作流实例到注册表
        WorkflowRunRegistry.register(chat_record_id_str, str(chat_info.chat_id), work_flow_manage)

        chat_info.set_chat(message)

        if stream:

            def generate():
                work_flow_manage.run()
                while True:
                    msg_type, data = result_queue.get()
                    if msg_type == "done":
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "error":
                        yield (
                            "data: "
                            + json.dumps(
                                {
                                    "chat_id": str(chat_info.chat_id),
                                    "chat_record_id": chat_record_id_str,
                                    "content": [{"type": "FAILURE", "content": str(data)}],
                                },
                                ensure_ascii=False,
                            )
                            + "\n\n"
                        )
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "chunk":
                        data["chat_id"] = str(chat_info.chat_id)
                        data["chat_record_id"] = chat_record_id_str
                        yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"

            return to_stream_response_simple(generate())
        else:
            work_flow_manage.run()
            while True:
                msg_type, data = result_queue.get()
                if msg_type == "done":
                    break
                if msg_type == "error":
                    raise data
            return base_to_response.to_block_response(chat_info.chat_id, chat_record_id_str, "", True, 0, 0)

    @staticmethod
    def save_chat_record(chat_info, chat_id, chat_record_id, question):
        chat_record = ChatRecord(
            id=chat_record_id,
            chat_id=chat_id,
            problem_text="",
            answer_text="",
            details={},
            message_tokens=0,
            answer_tokens=0,
            answer_text_list=[[]],
            run_time=0,
            index=len(chat_info.chat_record_list) + 1,
            ip_address=chat_info.ip_address,
            source=chat_info.source,
            workflow_context={},
            question=question,
            messages=[],
        )
        chat_info.append_chat_record(chat_record)
        chat_info.set_cache()

    @staticmethod
    def update_chat_record(chat_info, chat_id, chat_record_id, workflow_context, messages):
        message_tokens = sum(
            v.get("message_tokens", 0)
            for v in workflow_context.values()
            if isinstance(v, dict) and "message_tokens" in v
        )
        answer_tokens = sum(
            v.get("answer_tokens", 0) for v in workflow_context.values() if isinstance(v, dict) and "answer_tokens" in v
        )
        ChatUserTokenQuota.consume(chat_info.chat_user_id, message_tokens + answer_tokens)
        QuerySet(ChatRecord).filter(id=chat_record_id).update(
            workflow_context=workflow_context,
            messages=messages,
            message_tokens=message_tokens,
            answer_tokens=answer_tokens,
        )

    def is_valid_chat_user(self):
        chat_user_id = self.data.get("chat_user_id")
        application_id = self.data.get("application_id")
        chat_user_type = self.data.get("chat_user_type")
        is_auth_chat_user = DatabaseModelManage.get_model("is_auth_chat_user")
        application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application_id).first()
        if (
            application_access_token
            and application_access_token.authentication
            and application_access_token.authentication_value.get("type") == "login"
        ):
            if chat_user_type == ChatUserType.ANONYMOUS_USER.value:
                raise ChatException(500, _("The chat user is not authorized."))
            if chat_user_type == ChatUserType.CHAT_USER.value and is_auth_chat_user:
                is_auth = is_auth_chat_user(chat_user_id, application_id)
                if not is_auth:
                    raise ChatException(500, _("The chat user is not authorized."))

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        super().is_valid(raise_exception=True)
        ChatMessageSerializers(data=instance).is_valid(raise_exception=True)
        chat_info = self.get_chat_info()
        chat_info.get_application()
        chat_info.get_chat_user(asker=(instance.get("form_data") or {}).get("asker"))
        self.is_valid_chat_id(chat_info)
        if not self.data.get("debug"):
            self.is_valid_chat_user()
        ChatUserTokenQuota.consume(chat_info.chat_user_id, 0)  # 触发周期重置 + 配额预校验
        if chat_info.application.type == ApplicationTypeChoices.SIMPLE:
            self.is_valid_application_simple(raise_exception=True, chat_info=chat_info)
            return self.chat_simple(chat_info, instance, base_to_response)
        else:
            self.is_valid_application_workflow(raise_exception=True)
            return self.chat_work_flow(chat_info, instance, base_to_response)

    def get_chat_info(self):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get("chat_id")
        chat_info: ChatInfo = ChatInfo.get_cache(chat_id)
        if chat_info is None:
            chat_info: ChatInfo = self.re_open_chat(chat_id)
            chat_info.set_cache()
        return chat_info

    def re_open_chat(self, chat_id: str):
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is None:
            raise ChatException(500, _("Conversation does not exist"))
        application = QuerySet(Application).filter(id=chat.application_id).first()
        if application is None:
            raise ChatException(500, _("Application does not exist"))
        application_version = (
            QuerySet(ApplicationVersion).filter(application_id=application.id).order_by("-create_time")[0:1].first()
        )
        if application_version is None:
            raise ChatException(500, _("The application has not been published. Please use it after publishing."))
        if application.type == ApplicationTypeChoices.SIMPLE:
            return self.re_open_chat_simple(chat_id, application)
        else:
            return self.re_open_chat_work_flow(chat_id, application)

    def re_open_chat_simple(self, chat_id, application):
        if self.data.get("debug"):
            # 数据集id列表
            knowledge_id_list = [
                str(row.target_id)
                for row in QuerySet(ResourceMapping).filter(
                    source_id=str(application.id), source_type="APPLICATION", target_type="KNOWLEDGE"
                )
            ]
        else:
            application_version = (
                QuerySet(ApplicationVersion).filter(application_id=application.id).order_by("-create_time")[0:1].first()
            )
            knowledge_id_list = application_version.knowledge_ids

        # 需要排除的文档
        exclude_document_id_list = [
            str(document.id)
            for document in QuerySet(Document).filter(knowledge_id__in=knowledge_id_list, is_active=False)
        ]
        chat_info = ChatInfo(
            chat_id,
            self.data.get("chat_user_id"),
            self.data.get("chat_user_type"),
            self.data.get("ip_address"),
            self.data.get("source"),
            knowledge_id_list,
            exclude_document_id_list,
            application.id,
        )
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by("-create_time")[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info

    def re_open_chat_work_flow(self, chat_id, application):
        chat_info = ChatInfo(
            chat_id,
            self.data.get("chat_user_id"),
            self.data.get("chat_user_type"),
            self.data.get("ip_address"),
            self.data.get("source"),
            [],
            [],
            application.id,
        )
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by("-create_time")[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info


# consume 桥接队列的上限：满了会反压 pump 线程，防止慢客户端把消息全堆进内存
_BRIDGE_MAXSIZE = 1000
# 消费上限（秒），与桥接 get 的超时保持一致的量级
_CONSUME_TIMEOUT = 300


class ResumeSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True)
    chat_record_id = serializers.UUIDField(required=True)

    def resume(self, request):
        self.is_valid(raise_exception=True)
        from application.workflow.message_queue import get_message_queue
        from application.models import ChatRecord

        chat_record_id = self.data.get("chat_record_id")
        mq = get_message_queue()

        start_id = self._resolve_start_id(request)

        is_running = mq.exists(chat_record_id) and not mq.is_done(chat_record_id)

        if is_running:
            generator = self._stream_from_queue(mq, chat_record_id, start_id)
        else:
            chat_record = ChatRecord.objects.filter(id=chat_record_id).first()
            if not chat_record:
                return result.error(_("Chat record not found"))
            generator = self._stream_from_db(chat_record, start_id)

        response = StreamingHttpResponse(
            generator,
            content_type="text/event-stream;charset=utf-8",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

    @staticmethod
    def _resolve_start_id(request: Request) -> str:
        """
        优先取 SSE 标准的 Last-Event-ID 头（浏览器 EventSource 断线重连会自动带上），
        兼容 body / query 里显式传的 last_event_id。取不到则从头开始。
        """
        candidate = (
            request.META.get("HTTP_LAST_EVENT_ID")
            or (request.data.get("last_event_id") if hasattr(request, "data") else None)
            or request.query_params.get("last_event_id")
        )
        candidate = (candidate or "").strip()
        return candidate or "0"

    @staticmethod
    def _sse(msg_id: str, msg_data: str) -> str:
        """
        带 id 字段的 SSE 帧：浏览器会把最后收到的 id 存进 Last-Event-ID，
        下次重连自动回传，从而实现断点续传。
        """
        return f"id: {msg_id}\ndata: {msg_data}\n\n"

    def _stream_from_queue(self, mq, chat_record_id: str, start_id: str):
        """
        用后台线程跑阻塞式 consume，把回调桥接成 generator。
        复用 consume 已经处理好的 done 标记 / 尾部残留竞态，视图层不再重写收尾。
        """
        bridge: thread_queue.Queue = thread_queue.Queue(maxsize=_BRIDGE_MAXSIZE)
        done_sentinel = object()
        stop_event = threading.Event()

        def pump():
            try:
                mq.consume(
                    queue_id=chat_record_id,
                    start_id=start_id,
                    # bridge.put 无 timeout：队列满时在此反压，等 generator 消费腾位
                    on_message=lambda mid, data: bridge.put((mid, data)),
                    on_done=lambda: bridge.put(done_sentinel),  # 契约保证有且仅一次
                    timeout=_CONSUME_TIMEOUT,
                    should_stop=stop_event.is_set,  # 客户端断开时提前结束，省掉空转
                )
            except Exception as e:
                maxkb_logger.error(f"ResumeStream pump error [{chat_record_id}]: {e}")
                # 兜底：即使 consume 内部异常也要放哨兵，避免 generator 永久阻塞
                try:
                    bridge.put_nowait(done_sentinel)
                except thread_queue.Full:
                    pass

        worker = threading.Thread(target=pump, name=f"resume-{chat_record_id}", daemon=True)
        worker.start()

        try:
            while True:
                try:
                    # 略大于 consume timeout：正常情况下哨兵会先到，这里只防线程异常挂死
                    item = bridge.get(timeout=_CONSUME_TIMEOUT + 5)
                except thread_queue.Empty:
                    maxkb_logger.warning(f"ResumeStream bridge idle timeout [{chat_record_id}]")
                    break
                if item is done_sentinel:
                    break
                msg_id, msg_data = item
                yield self._sse(msg_id, msg_data)
            yield "data: [DONE]\n\n"
        finally:
            # 客户端提前关闭连接会在 yield 处抛 GeneratorExit，落到这里；
            # 通知 consume 线程停止，不必再等到 300s 超时
            stop_event.set()

    def _stream_from_db(self, chat_record, start_id: str):
        """
        已完成 / 不存在于队列：从库里读。
        若带了 Last-Event-ID，则跳过已发送过的部分（按落库时的消息 id 对齐）。
        """
        try:
            messages = chat_record.messages or []
            resuming = start_id and start_id != "0"
            passed = not resuming  # 无续传点则全部下发

            for msg in messages:
                msg_id = str(msg.get("id", "")) if isinstance(msg, dict) else ""

                if not passed:
                    # 尚未越过续传点：命中该 id 后，从下一条开始发
                    if msg_id and msg_id == start_id:
                        passed = True
                    continue

                yield self._sse(msg_id, json.dumps(msg, ensure_ascii=False))

            # 续传点在库里没匹配到（比如 id 体系不一致）：退化为整段重放，别让客户端收到空流
            if not passed:
                for msg in messages:
                    msg_id = str(msg.get("id", "")) if isinstance(msg, dict) else ""
                    yield self._sse(msg_id, json.dumps(msg, ensure_ascii=False))
        finally:
            yield "data: [DONE]\n\n"


class OpenChatSerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True)
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    debug = serializers.BooleanField(required=True, label=_("Debug"))
    ip_address = serializers.CharField(required=False, label=_("IP Address"))
    source = serializers.JSONField(required=False, label=_("Source"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        application_id = self.data.get("application_id")
        query_set = QuerySet(Application).filter(id=application_id)
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, gettext("Application does not exist"))

    def open(self, chat_id=None):
        self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).get(id=application_id)
        debug = self.data.get("debug")
        if not debug:
            application_version = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
            if application_version is None:
                raise AppApiException(500, _("The application has not been published. Please use it after publishing."))
        if application.type == ApplicationTypeChoices.SIMPLE:
            return self.open_simple(application, chat_id)
        else:
            return self.open_work_flow(application, chat_id)

    def open_work_flow(self, application, chat_id=None):
        self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        debug = self.data.get("debug")
        chat_id = chat_id or str(uuid.uuid7())
        chat_info = ChatInfo(chat_id, chat_user_id, chat_user_type, ip_address, source, [], [], application_id, debug)
        chat_info.save_chat()
        chat_info.set_cache()
        return chat_id

    def open_simple(self, application, chat_id=None):
        application_id = self.data.get("application_id")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        debug = self.data.get("debug")
        if debug:
            knowledge_id_list = [
                str(row.target_id)
                for row in QuerySet(ResourceMapping).filter(
                    source_id=str(application_id), source_type="APPLICATION", target_type="KNOWLEDGE"
                )
            ]
        else:
            application_version = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
            knowledge_id_list = application_version.knowledge_ids

        chat_id = chat_id or str(uuid.uuid7())
        chat_info = ChatInfo(
            chat_id,
            chat_user_id,
            chat_user_type,
            ip_address,
            source,
            knowledge_id_list,
            [
                str(document.id)
                for document in QuerySet(Document).filter(knowledge_id__in=knowledge_id_list, is_active=False)
            ],
            application_id,
            debug=debug,
        )
        chat_info.save_chat()
        chat_info.set_cache()
        return chat_id


class TextToSpeechSerializers(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    def text_to_speech(self, instance):
        self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).filter(id=application_id).first()
        return ApplicationOperateSerializer(
            data={"application_id": application_id, "user_id": application.user_id}
        ).text_to_speech(instance, False)


class SpeechToTextSerializers(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    def speech_to_text(self, instance):
        self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).filter(id=application_id).first()
        return ApplicationOperateSerializer(
            data={"application_id": application_id, "user_id": application.user_id}
        ).speech_to_text(instance, False)
