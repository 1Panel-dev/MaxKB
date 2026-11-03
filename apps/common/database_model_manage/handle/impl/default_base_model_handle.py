# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： default_base_model_handle.py
@date：2025/4/15 11:20
@desc:
"""

from typing import List

from django.db.models import QuerySet

from common.database_model_manage.handle.base_handle import IBaseModelHandle
from system_manage.models import (
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroupRelation,
)


def get_knowledge_list_of_authorized(chat_user_id, knowledge_id_list: List):
    """
    从 knowledge_id_list 中筛出对话用户被授权（直接授权或所在用户组授权）的知识库 id
    """
    knowledge_id_list = [str(knowledge_id) for knowledge_id in knowledge_id_list]
    group_id_list = QuerySet(UserGroupRelation).filter(user_id=chat_user_id).values_list("group_id", flat=True)
    # 通过对话用户组授权的知识库id
    auth_knowledge_id_by_group_list = [
        str(resource_id)
        for resource_id in QuerySet(ResourceChatUserGroupAuthorize)
        .filter(
            user_group_id__in=group_id_list,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id__in=knowledge_id_list,
            is_auth=True,
        )
        .values_list("resource_id", flat=True)
    ]
    # 通过对话用户直接授权的知识库id
    auth_knowledge_id_by_user_list = [
        str(resource_id)
        for resource_id in QuerySet(ResourceChatUserAuthorize)
        .filter(
            user_id=chat_user_id, resource_type=ResourceType.KNOWLEDGE, resource_id__in=knowledge_id_list, is_auth=True
        )
        .values_list("resource_id", flat=True)
    ]
    authorized = {*auth_knowledge_id_by_group_list, *auth_knowledge_id_by_user_list}
    return [knowledge_id for knowledge_id in knowledge_id_list if knowledge_id in authorized]


class DefaultBaseModelHandle(IBaseModelHandle):
    def get_model_dict(self):
        return {"get_knowledge_list_of_authorized": get_knowledge_list_of_authorized}
