# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    file_access.py
@date:    2026/11/25
@desc:    工作流节点读取文件的统一鉴权:只允许读取发起者本人的文件,或发起请求的根资源(应用/知识库/工具)的文件
"""

from django.db.models import QuerySet

from application.workflow.common import WorkflowType
from common.exception.app_exception import AppUnauthorizedFailed
from common.utils.common import is_valid_uuid
from knowledge.models import Document, File, FileSourceType, Paragraph
from system_manage.models.resource_mapping import ResourceMapping, ResourceType

ROOT_KEYS = ("root_user_type", "root_user_id", "root_workflow_type", "root_resource_id", "root_chat_id")
# 工作流运行中生成的 TOOL 文件标记:OSS 不将其视为公开文件(工具图标等仍公开)
WORKFLOW_GENERATED = "workflow_generated"


def root_context(user_type, user_id, workflow_type: WorkflowType, resource_id, chat_id=None):
    """
    工作流发起者身份与根资源:只在入口由服务端写入一次,子工作流(子应用/工具工作流,任意层嵌套)原样继承,
    不可被请求体或模型参数覆盖
    """
    return {
        "root_user_type": user_type,
        "root_user_id": str(user_id) if user_id else None,
        "root_workflow_type": workflow_type.value,
        "root_resource_id": str(resource_id) if resource_id else None,
        "root_chat_id": str(chat_id) if chat_id else None,
    }


def generated_file_target(workflow_params):
    workflow_params = workflow_params or {}
    root_workflow_type = workflow_params.get("root_workflow_type")
    resource_id = workflow_params.get("root_resource_id")
    chat_id = workflow_params.get("root_chat_id")
    user_id = workflow_params.get("root_user_id")
    if not root_workflow_type:
        for _type, key in (
            (WorkflowType.KNOWLEDGE, "knowledge_id"),
            (WorkflowType.APPLICATION, "application_id"),
            (WorkflowType.TOOL, "tool_id"),
        ):
            if workflow_params.get(key):
                root_workflow_type, resource_id = _type.value, workflow_params.get(key)
                break
        chat_id, user_id = workflow_params.get("chat_id"), user_id or workflow_params.get("chat_user_id")
    meta = {"debug": False, "user_id": user_id}
    if root_workflow_type == WorkflowType.APPLICATION.value:
        return FileSourceType.CHAT.value, chat_id, {**meta, "chat_id": chat_id, "application_id": resource_id}
    if root_workflow_type == WorkflowType.KNOWLEDGE.value:
        return FileSourceType.KNOWLEDGE.value, resource_id, {**meta, "knowledge_id": resource_id}
    if root_workflow_type == WorkflowType.TOOL.value and not workflow_params.get("debug"):
        return FileSourceType.TOOL.value, resource_id, {**meta, "tool_id": resource_id, WORKFLOW_GENERATED: True}
    temporary = FileSourceType.TEMPORARY_120_MINUTE.value
    return temporary, temporary, {**meta, "debug": True, "tool_id": resource_id}


def save_generated_file(file, workflow_params):
    """保存工作流运行中生成的文件(图片/音频/视频等),返回文件地址"""
    from oss.serializers.file import FileSerializer

    source_type, source_id, meta = generated_file_target(workflow_params)
    return FileSerializer(
        data={"file": file, "meta": meta, "source_id": source_id, "source_type": source_type}
    ).upload()


def _deny():
    raise AppUnauthorizedFailed(403, "No permission to access")


def _get_file_knowledge_id(file):
    if file.source_type == FileSourceType.KNOWLEDGE:
        return file.source_id
    if file.source_type == FileSourceType.DOCUMENT:
        return QuerySet(Document).filter(id=file.source_id).values_list("knowledge_id", flat=True).first()
    if file.source_type == FileSourceType.PARAGRAPH:
        return QuerySet(Paragraph).filter(id=file.source_id).values_list("knowledge_id", flat=True).first()
    return None


def _is_knowledge_bound(resource_type, resource_id, knowledge_id):
    """根应用/工具关联(ResourceMapping)的知识库,与 OSS 对关联知识库文件的放行规则一致"""
    return (
        QuerySet(ResourceMapping)
        .filter(
            source_type=resource_type,
            source_id=str(resource_id),
            target_type=ResourceType.KNOWLEDGE,
            target_id=str(knowledge_id),
        )
        .exists()
    )


def _in_root_resource(file, workflow_params):
    resource_type = {
        WorkflowType.APPLICATION.value: ResourceType.APPLICATION,
        WorkflowType.KNOWLEDGE.value: ResourceType.KNOWLEDGE,
        WorkflowType.TOOL.value: ResourceType.TOOL,
    }.get(workflow_params.get("root_workflow_type"))
    resource_id = workflow_params.get("root_resource_id")
    if resource_type is None or not resource_id:
        return False
    if file.source_type == FileSourceType.APPLICATION:
        root_chat_id = workflow_params.get("root_chat_id")
        return (
            resource_type == ResourceType.APPLICATION
            and str(file.source_id) == str(resource_id)
            and (file.meta or {}).get("chat_id") in (None, root_chat_id)
        )
    if file.source_type == FileSourceType.TOOL:
        return resource_type == ResourceType.TOOL and str(file.source_id) == str(resource_id)
    knowledge_id = _get_file_knowledge_id(file)
    if knowledge_id is None:
        return False
    if resource_type == ResourceType.KNOWLEDGE:
        return str(knowledge_id) == str(resource_id)
    return _is_knowledge_bound(resource_type, resource_id, knowledge_id)


def get_authorized_file(file_id, workflow_params):
    """
    工作流节点读取文件的唯一入口。允许:
    1. 发起者本人上传的文件,或本次运行(含嵌套子工作流)生成的文件
    2. 根资源的文件(应用当前对话的文件、知识库文件、根应用/工具关联知识库的文件),
       但他人运行时生成的工具/应用文件除外
    """
    workflow_params = workflow_params or {}
    file_id = str(file_id) if file_id else ""
    file = QuerySet(File).filter(id=file_id).first() if is_valid_uuid(file_id) else None
    if file is None:
        _deny()
    meta = file.meta or {}
    root_user_id = workflow_params.get("root_user_id")
    if root_user_id and str(meta.get("user_id")) == root_user_id:
        return file
    # 工具/应用运行时生成的文件归属于发起者;知识库文件属于知识库共享内容,仍按资源放行
    if meta.get("user_id") and file.source_type in (FileSourceType.TOOL, FileSourceType.APPLICATION):
        _deny()
    if file.source_type == FileSourceType.SYSTEM or _in_root_resource(file, workflow_params):
        return file
    _deny()
