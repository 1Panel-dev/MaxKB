# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    application.py
@date:    2026/9/15 16:10
@desc:
"""

import re
import threading

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from langchain_core.tools import StructuredTool
from pydantic import Field

from .base import build_schema


def _application_string_to_uuid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))


def get_application_args():
    """
    应用（Agent）工具对模型暴露的入参：固定单个必填 message。

    与 chat.mcp.tools.MCPToolHandler.list_tools 的 inputSchema 保持一致，
    这样从远端 MCP 代理切换为进程内直调时，模型侧契约不变。
    """
    return build_schema(
        {
            "message": (str, Field(..., required=True, description="The message to send to the AI.")),
        }
    )


def get_application_func(source_type, source_id, application, workflow_params, workspace_id):
    """
    构建应用（Agent）工具的执行函数。

    工具调用是同步的，不支持子应用表单中断，命中表单时返回已累积文本。
    """
    application_id = str(application.id)

    def inner(message: str = ""):
        from application.models import Application, ApplicationVersion, Chat, ChatRecord, ChatSourceChoices
        from application.workflow.common import WorkflowType, new_instance
        from application.workflow.content_type import ContentType
        from application.workflow.nodes import get_start_node
        from application.workflow.workflow_manage import CallBack, WorkflowManage
        from chat.serializers.chat import get_work_flow
        from chat.serializers.chat_history import ChatHistory

        question = str(message or "")
        chat_id = workflow_params.get("chat_id")
        chat_user_id = workflow_params.get("chat_user_id")
        chat_user_type = workflow_params.get("chat_user_type")
        ip_address = workflow_params.get("ip_address") or "-"
        source = workflow_params.get("source") or {"type": ChatSourceChoices.ONLINE.value}
        debug = workflow_params.get("debug", False)

        # 自引用守卫：子应用不能是当前应用本身
        if application_id == str(workflow_params.get("application_id") or ""):
            raise Exception("The sub application cannot use the current agent")

        # 派生子应用聊天 id（父对话 + 子应用稳定映射），与 application_node 一致
        current_chat_id = _application_string_to_uuid(str(chat_id) + application_id)
        asker = workflow_params.get("chat_user")
        Chat.objects.get_or_create(
            id=current_chat_id,
            defaults={
                "application_id": application_id,
                "abstract": question[0:1024],
                "chat_user_id": chat_user_id,
                "chat_user_type": chat_user_type,
                "ip_address": ip_address,
                "source": source,
                "asker": asker,
            },
        )

        # 解析子应用工作流（debug 取本体，否则取最新发布版本）
        if debug:
            sub_application = QuerySet(Application).filter(id=application_id).first()
        else:
            sub_application = (
                QuerySet(ApplicationVersion).filter(application_id=application_id).order_by("-create_time")[0:1].first()
            )
        if sub_application is None:
            raise Exception("The application has not been published. Please use it after publishing.")

        sub_workflow = new_instance(get_work_flow(sub_application), WorkflowType.APPLICATION)

        # 生成子应用记录 id 并建 ChatRecord（子对话可追溯）
        sub_chat_record_id = str(uuid.uuid7())
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

        # 组装子应用参数（复制父工作流参数并覆盖子应用相关字段）
        sub_parameters = dict(workflow_params)
        sub_parameters.update(
            {
                "chat_id": current_chat_id,
                "chat_record_id": sub_chat_record_id,
                "application_id": application_id,
                "question": question,
                "stream": True,
                "form_data": {},
                "position": None,
                "history_chat_record": ChatHistory(current_chat_id).load(exclude_record_id=sub_chat_record_id),
                "image_list": [],
                "document_list": [],
                "audio_list": [],
                "video_list": [],
                "default_model_setting": sub_application.default_model_setting or {},
            }
        )

        done_event = threading.Event()
        result_holder = {"answer": "", "error": None}

        def on_next(wf_manage, content):
            # 逐块聚合子应用文本回答（不直接转发给上游，作为工具结果一次性返回）
            if content.type == ContentType.TEXT:
                result_holder["answer"] += content.content or ""

        def on_complete(wf_manage, error):
            try:
                # 持久化子应用上下文，供后续追溯
                QuerySet(ChatRecord).filter(id=sub_chat_record_id).update(workflow_context=wf_manage.context)
            finally:
                result_holder["error"] = error
                done_event.set()

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            return get_start_node(wf, wm, WorkflowType.APPLICATION, None)

        sub_manage = WorkflowManage(
            sub_workflow, sub_parameters, WorkflowType.APPLICATION, call_back, get_start_node_fn
        )
        sub_manage.start_node.workflow_manage = sub_manage
        sub_manage.run()
        done_event.wait()
        if result_holder["error"]:
            raise result_holder["error"]

        answer = result_holder["answer"]
        # 去除 <tool_calls_render></tool_calls_render> 标签（与 MCPToolHandler.call_tool 一致）
        answer = re.sub(r"<tool_calls_render>.*?</tool_calls_render>", "", answer, flags=re.DOTALL)
        return answer

    return inner


def get_application_tools(source_type, source_id, application_ids, workspace_id, workflow_params):
    if not application_ids:
        return []
    from application.models import Application

    applications = QuerySet(Application).filter(id__in=application_ids, is_publish=True)
    results = []
    for application in applications:
        func = get_application_func(source_type, source_id, application, workflow_params, workspace_id)
        args = get_application_args()
        structured_tool = StructuredTool.from_function(
            func=func,
            name=application.name,
            description=f"{application.name} {application.desc or ''}".strip(),
            args_schema=args,
        )
        results.append(structured_tool)

    return results
