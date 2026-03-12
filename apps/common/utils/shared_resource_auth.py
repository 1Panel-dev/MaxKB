"""
    @project: MaxKB-xpack-ee
    @Author: niu
    @file: shared_resource_auth.py
    @date: 2026/3/11 11:22
    @desc:
"""
from typing import List

from django.db.models import QuerySet

from common.database_model_manage.database_model_manage import DatabaseModelManage
from knowledge.models import Knowledge
from tools.models import Tool


def filter_authorized_ids(resource_type: str, ids: List[str], workspace_id: str) -> List[str]:
    """
    通用授权过滤函数

    @param resource_type: 资源类型 ('model', 'tool', 'knowledge')
    @param ids: 待过滤的ID列表
    @param workspace_id: 工作空间ID
    @return: 授权通过的ID列表
    """

    if not ids:
        return []

    auth_func = DatabaseModelManage.get_model(f"get_authorized_{resource_type}")

    model_class = {'tool': Tool, 'knowledge': Knowledge}.get(resource_type)
    if model_class is None:
        return ids

    same_workspace_ids = list(
        QuerySet(model_class).filter(id__in=ids, workspace_id=workspace_id)
        .values_list('id', flat=True)
    )

    cross_workspace_ids = [i for i in ids if i not in set(map(str, same_workspace_ids))]

    authorized_ids = set(map(str, same_workspace_ids))

    if cross_workspace_ids and auth_func is not None:
        cross_queryset = QuerySet(model_class).filter(id__in=cross_workspace_ids)
        authorized = auth_func(cross_queryset, workspace_id)
        authorized_ids.update(str(r.id) for r in authorized)

    return [i for i in ids if i in authorized_ids]