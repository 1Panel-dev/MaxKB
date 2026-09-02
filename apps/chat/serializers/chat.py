# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： chat.py
@date：2025/6/9 11:23
@desc: 对话新实现（统一走 workflow 引擎、去除 ChatInfo 与 Redis 会话缓存）。
"""

import json
import os
import queue
import queue as thread_queue
import threading

import uuid_utils
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rest_framework import serializers
from rest_framework.request import Request

from application.flow.tools import to_stream_response_simple
from application.models import (
    Application,
    ApplicationVersion,
    ApplicationAccessToken,
    ApplicationChatUserStats,
    Chat,
    ChatRecord,
    ChatUserType,
    ExecuteType,
)
from application.serializers.application import ApplicationOperateSerializer
from application.serializers.application_chat import ChatCountSerializer
from application.serializers.common import resolve_chat_user, resolve_chat_user_group
from chat.serializers.chat_history import ChatHistory
from application.workflow.common import WorkflowType, new_instance
from application.workflow.message.aggregator import AggregationManager
from application.workflow.message.struct.failure_content import FailureContent
from application.workflow.message_queue import get_message_queue
from application.workflow.nodes import get_start_node
from application.workflow.workflow_manage import WorkflowManage, CallBack
from application.workflow.workflow_run_registry import WorkflowRunRegistry
from chat.template.agent_simple import build_workflow
from common import result
from common.exception.app_exception import AppApiException, AppChatNumOutOfBoundsFailed, ChatException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import get_file_content
from common.utils.logger import maxkb_logger
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model, Status
from models_provider.tools import get_model_instance_by_model_workspace_id
from system_manage.models.chat_user_token_quota import ChatUserTokenQuota

_CHAT_UNSET = object()


def get_work_flow(application):
    if application.type == "WORK_FLOW":
        return application.work_flow
    return build_workflow(application)


class ChatMessageSerializers(serializers.Serializer):
    """新流程的对话入参（去掉旧工作流调试字段 node_id/runtime_node_id/node_data/child_node）。"""

    message = serializers.DictField(required=True, label=_("User Questions"))
    stream = serializers.BooleanField(required=False, default=True, label=_("Is the answer in streaming mode"))
    re_chat = serializers.BooleanField(required=False, default=False, label=_("Do you want to reply again"))
    chat_record_id = serializers.UUIDField(required=False, allow_null=True, label=_("Conversation record id"))
    form_data = serializers.DictField(required=False, label=_("Global variables"))
    # Form 提交时的定位信息 {id, index, children}
    position = serializers.DictField(required=False, allow_null=True, label=_("Form position"))
    chunk_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Chunk id"))


class DebugChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Client Type"))
    ip_address = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("IP Address"))
    source = serializers.JSONField(required=False, allow_null=True, label=_("Source"))

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        self.is_valid(raise_exception=True)
        return ChatSerializers(
            data={
                "chat_id": self.data.get("chat_id"),
                "chat_user_id": self.data.get("chat_user_id"),
                "chat_user_type": self.data.get("chat_user_type"),
                "application_id": self.data.get("application_id"),
                "ip_address": self.data.get("ip_address"),
                "source": self.data.get("source"),
                "debug": True,
            }
        ).chat(instance, base_to_response)


class ChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    application_id = serializers.UUIDField(required=True, allow_null=True, label=_("Application ID"))
    debug = serializers.BooleanField(required=False, label=_("Debug"))
    ip_address = serializers.CharField(required=False, label=_("IP Address"), allow_null=True, allow_blank=True)
    source = serializers.JSONField(required=False, label=_("Source"))

    # ---------- 会话行（一次查询，全程复用） ----------
    def get_chat(self):
        """查询 Chat 行并缓存到实例，全流程只查一次（区分未查询/不存在）。"""
        cached = getattr(self, "_chat_cache", _CHAT_UNSET)
        if cached is _CHAT_UNSET:
            cached = QuerySet(Chat).filter(id=self.data.get("chat_id")).first()
            self._chat_cache = cached
        return cached

    # ---------- 校验 ----------
    def is_valid_chat(self):
        """
        会话不存在 → 视为新会话，后续 ensure_chat_row 惰性创建，无需前端传标记；
        会话已存在 → 校验归属（必须属于当前应用与当前对话用户），防止越权写入。
        debug 会话同样落库(execute_type=DEBUG)、同样按此校验，不再特殊放行。
        """
        chat = self.get_chat()
        if chat is None:
            return
        if str(chat.application_id) != str(self.data.get("application_id")) or str(chat.chat_user_id) != str(
            self.data.get("chat_user_id")
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

    # ---------- application ----------
    def get_application(self):
        """debug 取 Application 本体；非 debug 取最新发布的 ApplicationVersion。"""
        application_id = self.data.get("application_id")
        if self.data.get("debug"):
            application = QuerySet(Application).filter(id=application_id).first()
            if application is None:
                raise ChatException(500, _("The application does not exist"))
        else:
            application = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
            if application is None:
                raise ChatException(500, _("The application has not been published. Please use it after publishing."))
        return application

    def ensure_chat_row(self, question, asker):
        """Chat 行不存在则创建（debug 记为 DEBUG 类型），返回该行。复用 get_chat 的一次查询。"""
        chat = self.get_chat()
        if chat is not None:
            return chat
        chat = Chat(
            id=self.data.get("chat_id"),
            application_id=self.data.get("application_id"),
            abstract=(question or "")[0:1024],
            execute_type=ExecuteType.DEBUG if self.data.get("debug") else ExecuteType.CHAT,
            chat_user_id=self.data.get("chat_user_id"),
            chat_user_type=self.data.get("chat_user_type"),
            ip_address=self.data.get("ip_address"),
            source=self.data.get("source"),
            asker=asker,
        )
        chat.save()
        self._chat_cache = chat
        return chat

    def get_defaults_record(self, question):
        """构造一条占位 ChatRecord 的字段（workflow 完成后由 update_chat_record 回填）。"""
        return {
            "chat_id": self.data.get("chat_id"),
            "problem_text": "",
            "answer_text": "",
            "details": {},
            "message_tokens": 0,
            "answer_tokens": 0,
            "answer_text_list": [[]],
            "run_time": 0,
            # index 现在用不上，字段 NOT NULL 故给常量 0
            "index": 0,
            "ip_address": self.data.get("ip_address") or "",
            "source": self.data.get("source"),
            "workflow_context": {},
            "question": question,
            "messages": [],
        }

    @staticmethod
    def _usage_from_context(workflow_context):
        """从 workflow_context 汇总 token 用量：prompt=message_tokens, completion=answer_tokens。"""
        prompt_tokens = sum(
            v.get("message_tokens", 0)
            for v in workflow_context.values()
            if isinstance(v, dict) and "message_tokens" in v
        )
        completion_tokens = sum(
            v.get("answer_tokens", 0) for v in workflow_context.values() if isinstance(v, dict) and "answer_tokens" in v
        )
        return {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}

    @staticmethod
    def update_chat_record(chat_user_id, chat_record_id, workflow_context, messages):
        usage = ChatSerializers._usage_from_context(workflow_context)
        message_tokens = usage["prompt_tokens"]
        answer_tokens = usage["completion_tokens"]
        ChatUserTokenQuota.consume(chat_user_id, message_tokens + answer_tokens)
        QuerySet(ChatRecord).filter(id=chat_record_id).update(
            workflow_context=workflow_context,
            messages=messages,
            message_tokens=message_tokens,
            answer_tokens=answer_tokens,
        )

    # ---------- 执行 ----------
    def chat_work_flow(self, application, instance: dict, base_to_response):
        message_dict = instance.get("message")
        message = message_dict.get("content", "") if isinstance(message_dict, dict) else message_dict
        re_chat = instance.get("re_chat")
        stream = instance.get("stream")
        chat_id = self.data.get("chat_id")
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        form_data = instance.get("form_data") or {}
        image_list = message_dict.get("image_list", []) if isinstance(message_dict, dict) else []
        video_list = message_dict.get("video_list", []) if isinstance(message_dict, dict) else []
        document_list = message_dict.get("document_list", []) if isinstance(message_dict, dict) else []
        audio_list = message_dict.get("audio_list", []) if isinstance(message_dict, dict) else []
        other_list = message_dict.get("other_list", []) if isinstance(message_dict, dict) else []
        workspace_id = application.workspace_id
        chat_record_id = instance.get("chat_record_id")
        position = instance.get("position")
        chunk_id = instance.get("chunk_id")
        debug = self.data.get("debug", False)

        # 对话用户信息（asker 取自 form_data）
        chat_user = resolve_chat_user(chat_user_id, chat_user_type, asker=form_data.get("asker"))
        chat_user_group = resolve_chat_user_group(chat_user)

        history_chat_record = ChatHistory(chat_id).load(exclude_record_id=chat_record_id)

        work_flow = get_work_flow(application)
        workflow = new_instance(work_flow, WorkflowType.APPLICATION)

        chat_record_id_str = str(uuid.uuid7()) if chat_record_id is None else str(chat_record_id)
        self.ensure_chat_row(message, chat_user)
        if chat_record_id is None:
            ChatRecord(id=chat_record_id_str, **self.get_defaults_record(message_dict)).save(force_insert=True)

        parameters = {
            "history_chat_record": history_chat_record,
            "question": message,
            "chat_id": chat_id,
            "chat_record_id": chat_record_id_str,
            "stream": stream,
            "re_chat": re_chat,
            "chat_user_id": chat_user_id,
            "chat_user_type": chat_user_type,
            "ip_address": ip_address,
            "source": source,
            "workspace_id": workspace_id,
            "debug": debug,
            "chat_user": chat_user,
            "chat_user_group": chat_user_group,
            "application_id": str(self.data.get("application_id")),
            "form_data": form_data,
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

        def on_next(wf_manage, content):
            aggregation.aggregate(content)
            block = content.to_dict()
            get_message_queue().produce(chat_record_id_str, block)
            result_queue.put(("chunk", block))

        def on_complete(wf_manage, error):
            WorkflowRunRegistry.unregister(chat_record_id_str, str(chat_id))
            message_queue = get_message_queue()
            if error:
                result_queue.put(("error", error))
                message_queue.produce(
                    chat_record_id_str,
                    FailureContent(str(uuid_utils.uuid7()), str(error), Status.SUCCESS, None, None).to_dict(),
                )
            messages = aggregation.get_contents()
            self.update_chat_record(chat_user_id, chat_record_id_str, wf_manage.context, messages)
            ChatCountSerializer(data={"chat_id": chat_id}).update_chat()
            ChatHistory(chat_id).append(
                ChatRecord(
                    id=chat_record_id_str,
                    chat_id=chat_id,
                    question=message_dict,
                    messages=messages,
                    create_time=timezone.now(),
                )
            )
            result_queue.put(("done", None))
            message_queue.produce_done(chat_record_id_str)

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            return get_start_node(wf, wm, WorkflowType.APPLICATION, position)

        # Form 提交（有 position 和 chat_record_id）：从历史 context 恢复
        if position and chat_record_id:
            work_flow_manage = WorkflowManage.from_context(
                chat_record_id=chat_record_id,
                workflow=workflow,
                parameters=parameters,
                workflow_type=WorkflowType.APPLICATION,
                call_back=call_back,
                get_start_node=get_start_node_fn,
            )
            if work_flow_manage is None:
                work_flow_manage = WorkflowManage(
                    workflow, parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
                )
        else:
            work_flow_manage = WorkflowManage(
                workflow, parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
            )

        work_flow_manage.start_node.workflow_manage = work_flow_manage
        WorkflowRunRegistry.register(chat_record_id_str, str(chat_id), work_flow_manage)

        if stream:

            def generate():
                work_flow_manage.run()
                while True:
                    msg_type, data = result_queue.get()
                    if msg_type == "done":
                        end_frame = base_to_response.to_stream_end(
                            chat_id,
                            chat_record_id_str,
                            usage=self._usage_from_context(work_flow_manage.context),
                        )
                        if end_frame is not None:
                            yield "data: " + end_frame + "\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "error":
                        error_block = {"id": str(uuid.uuid7()), "type": "FAILURE", "content": str(data)}
                        frame = base_to_response.to_stream(chat_id, chat_record_id_str, error_block)
                        if frame is not None:
                            yield "data: " + frame + "\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "chunk":
                        frame = base_to_response.to_stream(chat_id, chat_record_id_str, data)
                        if frame is not None:
                            yield "data: " + frame + "\n\n"

            return to_stream_response_simple(generate())
        else:
            work_flow_manage.run()
            while True:
                msg_type, data = result_queue.get()
                if msg_type == "done":
                    break
                if msg_type == "error":
                    raise data
            usage = self._usage_from_context(work_flow_manage.context)
            return base_to_response.to_block(chat_id, chat_record_id_str, aggregation.get_contents(), usage)

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        self.is_valid(raise_exception=True)
        ChatMessageSerializers(data=instance).is_valid(raise_exception=True)
        self.is_valid_chat()
        application = self.get_application()
        self.is_valid_intraday_access_num()
        return self.chat_work_flow(application, instance, base_to_response)


class OpenAIMessage(serializers.Serializer):
    content = serializers.CharField(required=True, label=_("content"))
    role = serializers.CharField(required=True, label=_("Role"))


class OpenAIInstanceSerializer(serializers.Serializer):
    messages = serializers.ListField(child=OpenAIMessage())
    chat_id = serializers.UUIDField(required=False, label=_("Conversation ID"))
    re_chat = serializers.BooleanField(required=False, label=_("Regenerate"))
    stream = serializers.BooleanField(required=False, label=_("Streaming Output"))


class OpenAIChatSerializer(serializers.Serializer):
    """OpenAI 兼容入口：走新 ChatSerializers + OpenaiToResponse，无 ChatInfo/缓存。"""

    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    ip_address = serializers.CharField(required=False, label=_("IP Address"))
    source = serializers.JSONField(required=False, label=_("Source"))

    @staticmethod
    def get_message(instance):
        return instance.get("messages")[-1].get("content")

    def chat(self, instance: dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            OpenAIInstanceSerializer(data=instance).is_valid(raise_exception=True)
        # 会话不存在则新开：新 ChatSerializers 会按 chat_id 惰性建 Chat 行，无需缓存
        chat_id = instance.get("chat_id") or str(uuid.uuid7())
        message = self.get_message(instance)
        return ChatSerializers(
            data={
                "chat_id": chat_id,
                "chat_user_id": self.data.get("chat_user_id"),
                "chat_user_type": self.data.get("chat_user_type"),
                "application_id": self.data.get("application_id"),
                "ip_address": self.data.get("ip_address"),
                "source": self.data.get("source"),
            }
        ).chat(
            {
                "message": {
                    "content": message,
                    "image_list": instance.get("image_list", []),
                    "document_list": instance.get("document_list", []),
                    "audio_list": instance.get("audio_list", []),
                    "video_list": instance.get("video_list", []),
                    "other_list": instance.get("other_list", []),
                },
                "re_chat": instance.get("re_chat", False),
                "stream": instance.get("stream", False),
                "form_data": instance.get("form_data", {}),
            },
            base_to_response=OpenaiToResponse(),
        )


# ==================== 会话创建 ====================


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
            raise AppApiException(500, _("Application does not exist"))

    def open(self, chat_id=None):
        """新建会话：直接建 Chat 行（cache-free，无 ChatInfo）。SIMPLE/WORK_FLOW 一视同仁。"""
        self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        debug = self.data.get("debug")
        if not debug:
            published = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
            if published is None:
                raise AppApiException(500, _("The application has not been published. Please use it after publishing."))
        chat_id = chat_id or str(uuid.uuid7())
        Chat(
            id=chat_id,
            application_id=application_id,
            abstract="新建对话",
            execute_type=ExecuteType.DEBUG if debug else ExecuteType.CHAT,
            chat_user_id=self.data.get("chat_user_id"),
            chat_user_type=self.data.get("chat_user_type"),
            ip_address=self.data.get("ip_address"),
            source=self.data.get("source"),
            asker=resolve_chat_user(self.data.get("chat_user_id"), self.data.get("chat_user_type")),
        ).save()
        return chat_id


# ==================== 断点续传 ====================

# consume 桥接队列的上限：满了会反压 pump 线程，防止慢客户端把消息全堆进内存
_BRIDGE_MAXSIZE = 1000
# 消费上限（秒），与桥接 get 的超时保持一致的量级
_CONSUME_TIMEOUT = 300


class ResumeSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True)
    chat_record_id = serializers.UUIDField(required=True)

    def resume(self, request):
        self.is_valid(raise_exception=True)
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


# ==================== 提示词生成 ====================

SYSTEM_ROLE = get_file_content(os.path.join(PROJECT_DIR, "apps", "chat", "template", "generate_prompt_system"))


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


# ==================== 语音 ====================


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
