# coding=utf-8
"""
@project: MaxKB
@file： application_node.py
@date：2026/9/3
@desc: 智能体节点
"""

import time
from copy import deepcopy

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, ApplicationVersion, Chat, ChatRecord, ChatSourceChoices
from application.workflow.common import WorkflowType, new_instance
from application.workflow.content_type import ContentType
from application.workflow.i_node import INode, Signal
from application.workflow.message.aggregator import AggregationManager
from application.workflow.message.struct.content import Position
from application.workflow.status import Status
from application.workflow.workflow_manage import WorkflowManage, CallBack
from chat.serializers.chat_history import ChatHistory
from common.exception.app_exception import AppApiException
from common.utils.logger import maxkb_logger
from system_manage.services.chat_user_authorization import ensure_workflow_application_chat_user_authorized


def string_to_uuid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))


class ApplicationNodeSerializer(serializers.Serializer):
    application_id = serializers.CharField(required=True, label=_("Application ID"))
    question_reference_address = serializers.ListField(required=True, label=_("User Questions"))
    api_input_field_list = serializers.ListField(required=False, label=_("API Input Fields"))
    user_input_field_list = serializers.ListField(required=False, label=_("User Input Fields"))
    image_list = serializers.ListField(required=False, label=_("picture"))
    document_list = serializers.ListField(required=False, label=_("document"))
    audio_list = serializers.ListField(required=False, label=_("Audio"))
    video_list = serializers.ListField(required=False, label=_("Video"))
    node_data = serializers.DictField(required=False, allow_null=True, label=_("Form Data"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        f_app = QuerySet(Application).filter(id=application_id).first()
        if f_app is None:
            raise AppApiException(500, _("The application has been deleted"))


class ApplicationNode(INode):
    serializer_class = ApplicationNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION]
    type = "application-node"

    def __init__(self, node, workflow_manage, get_node_parameters):
        super().__init__(node, workflow_manage, get_node_parameters)
        self._current_sub_manage = None

    def cancel(self):
        super().cancel()
        if self._current_sub_manage:
            self._current_sub_manage.cancel()

    def _run(self):
        # 完成时机由子应用 on_complete 回调驱动，这里不自动 complete
        self.execute()

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        application_id = node_params.get("application_id")
        chat_id = workflow_params.get("chat_id")
        chat_user_id = workflow_params.get("chat_user_id")
        chat_user_type = workflow_params.get("chat_user_type")
        ip_address = workflow_params.get("ip_address") or "-"
        source = workflow_params.get("source") or {"type": ChatSourceChoices.ONLINE.value}
        debug = workflow_params.get("debug", False)

        # 父工作流 position 指向本节点 → 子工作流表单提交，需恢复续跑
        position = workflow_params.get("position") or {}
        is_submit = position.get("id") == self.get_node_id()
        sub_chat_record_id = self.get_context("sub_chat_record_id")
        # 表单暂停点：前端回传的 position 是一个嵌套链（id=本节点, children=子工作流暂停点）。
        # 恢复时用 position.children 逐级下传，才能把深层锚点（子子工作流表单）完整带下去。
        sub_position = position.get("children") if is_submit else None

        # 自引用守卫
        if application_id == workflow_params.get("application_id"):
            raise Exception(_("The sub application cannot use the current node"))

        from application.serializers.application import validate_application_bindings

        validate_application_bindings(
            workflow_params.get("workflow_user_id"),
            workflow_params.get("workspace_id"),
            {"application_ids": [application_id]},
        )

        ensure_workflow_application_chat_user_authorized(application_id, workflow_params)

        # 解析用户问题
        question_address = node_params.get("question_reference_address") or []
        if question_address:
            question = self.workflow_manage.get_reference_field(question_address[0], question_address[1:])
        else:
            question = ""
        question = str(question or "")
        self.data["question"] = question

        # 解析 api 输入 / 用户输入 → form_data
        form_data = {}
        for api_input_field in node_params.get("api_input_field_list", []):
            value = api_input_field.get("value", [""])[0] if api_input_field.get("value") else ""
            form_data[api_input_field["variable"]] = (
                self.workflow_manage.get_reference_field(value, api_input_field["value"][1:]) if value != "" else ""
            )
        for user_input_field in node_params.get("user_input_field_list", []):
            value = user_input_field.get("value", [""])[0] if user_input_field.get("value") else ""
            form_data[user_input_field["field"]] = (
                self.workflow_manage.get_reference_field(value, user_input_field["value"][1:]) if value != "" else ""
            )

        # 解析文件列表（校验 file_id）
        app_document_list = self._resolve_file_list(node_params.get("document_list", []), "document")
        app_image_list = self._resolve_file_list(node_params.get("image_list", []), "image")
        app_audio_list = self._resolve_file_list(node_params.get("audio_list", []), "audio")
        app_video_list = self._resolve_file_list(node_params.get("video_list", []), "video")

        # 派生子应用聊天 id
        current_chat_id = string_to_uuid(chat_id + application_id)
        Chat.objects.get_or_create(
            id=current_chat_id,
            defaults={
                "application_id": application_id,
                "abstract": question[0:1024],
                "chat_user_id": chat_user_id,
                "chat_user_type": chat_user_type,
                "ip_address": ip_address,
                "source": source,
                "asker": self._get_chat_asker(workflow_params),
            },
        )

        # 解析子应用工作流（debug 取本体，否则取最新发布版本），与 chat_work_flow 的 get_application 一致
        if debug:
            sub_application = QuerySet(Application).filter(id=application_id).first()
        else:
            sub_application = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
        if sub_application is None:
            raise Exception(_("The application has not been published. Please use it after publishing."))
        from chat.serializers.chat import get_work_flow

        sub_workflow = new_instance(get_work_flow(sub_application), WorkflowType.APPLICATION)

        # 首次运行：生成子应用记录 id 并建 ChatRecord；恢复时沿用已持久化的 id
        if not is_submit:
            sub_chat_record_id = str(uuid.uuid7())
            self.write_context("sub_chat_record_id", sub_chat_record_id)
            QuerySet(ChatRecord).create(
                id=sub_chat_record_id,
                chat_id=current_chat_id,
                problem_text=question[0:1024],
                answer_text="",
                details={},
                message_tokens=0,
                answer_tokens=0,
                answer_text_list=[[]],
                index=0,
                ip_address=ip_address or "",
                source=source,
                workflow_context={},
                question={"content": question},
                messages=[],
            )
            # 新提问刷新子应用会话更新时间，子应用对话日志按 update_time 倒序展示
            QuerySet(Chat).filter(id=current_chat_id).update(update_time=timezone.now())

        # 组装子应用参数（复制父工作流参数并覆盖子应用相关字段）
        sub_parameters = dict(workflow_params)
        sub_parameters.update(
            {
                "chat_id": current_chat_id,
                "chat_record_id": sub_chat_record_id,
                "application_id": application_id,
                "workflow_user_id": workflow_params.get("workflow_user_id")
                if debug
                else sub_application.publish_user_id,
                "question": question,
                "stream": True,
                "form_data": workflow_params.get("form_data") if is_submit else form_data,
                "position": sub_position,
                "chunk_id": workflow_params.get("chunk_id"),
                "history_chat_record": ChatHistory(current_chat_id).load(exclude_record_id=sub_chat_record_id),
                "image_list": app_image_list,
                "document_list": app_document_list,
                "audio_list": app_audio_list,
                "video_list": app_video_list,
                "default_model_setting": sub_application.default_model_setting or {},
            }
        )

        # 内联回调：转发子应用输出、嵌套 position、传播表单暂停信号
        # 表单续跑：接上暂停前已输出的回答，避免 result 只剩表单之后的内容
        self._answer = (self.get_context("result") or "") if is_submit else ""
        self._reasoning_content = (self.get_context("reasoning_content") or "") if is_submit else ""

        sub_start_time = time.time()
        # 子应用自身记录的 messages：在改写 position 之前聚合，保留子应用内部的位置
        aggregation = AggregationManager()

        def on_next(wf_manage, content):
            aggregation.aggregate(deepcopy(content))
            # 所有块（含已提交表单的回显块，chunk_id 与原表单一致）都转发：前端与父记录 messages 均按 id 合并，
            # 据此把原表单更新为已提交状态；若丢弃，刷新后子应用表单仍显示未提交，可被重复提交
            content.position = Position(self.get_node_id(), None, content.position)
            if content.type == ContentType.TEXT:
                self._answer += content.content
            elif content.type == ContentType.REASONING:
                self._reasoning_content += content.content
            self.write(content)

        def on_complete(wf_manage, error):
            self._current_sub_manage = None
            usage = wf_manage.get_usage()
            self._write_final_context(self._answer, self._reasoning_content, usage)
            try:
                self._save_sub_chat_record(
                    wf_manage, sub_chat_record_id, current_chat_id, sub_position, aggregation, sub_start_time
                )
            except Exception as record_error:
                # 回调在子应用线程执行，保存失败也必须结束本节点，避免对话一直等待
                maxkb_logger.error(f"save sub application chat record error [{sub_chat_record_id}]: {record_error}")
                self.complete(Status.FAIL, error=error or record_error)
                return
            # 子应用被取消：如实以 CANCELLED 结束本节点
            if wf_manage.signal == Signal.CANCELLED or self.workflow_manage.signal == Signal.CANCELLED:
                self.complete(Status.CANCELLED)
                return
            if error:
                self.complete(Status.FAIL, error=error)
                return
            # 子应用命中表单（Signal.FORM）：向上传播中断，暂停父工作流，等用户提交后恢复
            if wf_manage.signal == Signal.FORM:
                self.complete(Status.SUCCESS, signal=Signal.FORM)
                return
            self.complete(Status.SUCCESS)

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            from application.workflow.nodes import get_start_node

            return get_start_node(wf, wm, WorkflowType.APPLICATION, sub_position)

        # 表单提交：从历史 context 恢复子应用；否则全新运行
        if is_submit:
            from application.serializers.common import load_debug_workflow_context

            sub_manage = WorkflowManage.from_context(
                get_context=lambda: load_debug_workflow_context(sub_chat_record_id),
                workflow=sub_workflow,
                parameters=sub_parameters,
                workflow_type=WorkflowType.APPLICATION,
                call_back=call_back,
                get_start_node=get_start_node_fn,
            )
            if sub_manage is None:
                sub_manage = WorkflowManage(
                    sub_workflow, sub_parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
                )
        else:
            sub_manage = WorkflowManage(
                sub_workflow, sub_parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
            )

        sub_manage.start_node.workflow_manage = sub_manage
        self._current_sub_manage = sub_manage
        # 取消发生在构造之后、启动之前：不再启动子应用
        if self.status == Status.CANCELLED or self.workflow_manage.signal == Signal.CANCELLED:
            self.complete(Status.CANCELLED)
            return
        sub_manage.run()

    def _resolve_file_list(self, field_list, name):
        if not field_list or len(field_list) == 0:
            return []
        values = self.workflow_manage.get_reference_field(field_list[0], field_list[1:]) or []
        for item in values:
            if "file_id" not in item:
                raise ValueError(
                    _("Parameter value error: The uploaded {name} lacks file_id, and the {name} upload fails").format(
                        name=name
                    )
                )
        return list(values)

    @staticmethod
    def _save_sub_chat_record(wf_manage, sub_chat_record_id, sub_chat_id, sub_position, aggregation, start_time):
        """
        子应用记录落库，与 chat_work_flow 的 on_complete 一致：
        workflow_context 供表单续跑的 from_context 读取；messages/details 供子应用对话日志展示。
        表单续跑时与旧记录按 id 合并 messages、按 position 合并 details。
        token 已计入父节点详情，由父对话统一扣减额度，这里不重复扣减。
        """
        from application.serializers.application_chat import ChatCountSerializer

        messages = aggregation.get_contents()
        old_details = None
        chat_record = QuerySet(ChatRecord).filter(id=sub_chat_record_id).first()
        if chat_record and sub_position:
            old_details = chat_record.details
            if chat_record.messages:
                messages = list({m.get("id"): m for m in [*chat_record.messages, *messages]}.values())
        details = wf_manage.get_details(position=sub_position, old_details=old_details)
        usage = wf_manage.get_usage()
        QuerySet(ChatRecord).filter(id=sub_chat_record_id).update(
            workflow_context=wf_manage.context,
            messages=messages,
            details=details,
            message_tokens=usage.get("prompt_tokens", 0),
            answer_tokens=usage.get("completion_tokens", 0),
            run_time=time.time() - start_time,
        )
        ChatCountSerializer(data={"chat_id": sub_chat_id}).update_chat()
        ChatHistory(sub_chat_id).append(
            ChatRecord(
                id=sub_chat_record_id,
                chat_id=sub_chat_id,
                question=chat_record.question if chat_record else None,
                messages=messages,
                details=details,
                create_time=timezone.now(),
            )
        )

    def _get_chat_asker(self, workflow_params):
        asker = (workflow_params.get("form_data") or {}).get("asker")
        if asker:
            return asker if isinstance(asker, dict) else {"username": asker}
        return workflow_params.get("chat_user")

    def _write_final_context(self, answer, reasoning_content, usage):
        self.write_context("result", answer)
        self.write_context("reasoning_content", reasoning_content)
        self.data["answer"] = answer
        self.data["reasoning_content"] = reasoning_content
        self.data["message_tokens"] = usage.get("prompt_tokens", 0)
        self.data["answer_tokens"] = usage.get("completion_tokens", 0)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.data.get("question"),
                "answer": self.data.get("answer"),
                "reasoning_content": self.data.get("reasoning_content"),
                "message_tokens": self.data.get("message_tokens"),
                "answer_tokens": self.data.get("answer_tokens"),
            }
        )
        return details
