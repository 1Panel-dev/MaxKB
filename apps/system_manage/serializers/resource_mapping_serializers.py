# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 17:17
    @desc:
"""
import json
import os

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_page_search, get_dynamics_model
from common.result import Page
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from system_manage.models.resource_mapping import ResourceMapping


class ResourceMappingSerializer(serializers.Serializer):
    resource = serializers.CharField(required=True, label=_('resource'))
    resource_id = serializers.UUIDField(required=True, label=_('resource Id'))
    resource_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('resource Name'))
    source_type = serializers.ListField(
        label=_('source Type'),
        child=serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('source Type')))
    user_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('creator'))
    workspace_ids = serializers.CharField(required=False, label=_('workspace_ids'))

    def get_query_set(self):
        queryset = QuerySet(model=get_dynamics_model({
            'sdc.name': models.CharField(),
            'target_id': models.CharField(),
            "target_type": models.CharField(),
            "u.username": models.CharField(),
            'rm.source_type': models.CharField(),
            'workspace_id': models.CharField(),
        }))

        queryset = queryset.filter(target_id=self.data.get('resource_id'),
                                   target_type=self.data.get('resource'))

        if self.data.get('resource_name'):
            queryset = queryset.filter(**{'sdc.name__icontains': self.data.get('resource_name')})
        if self.data.get('user_name'):
            queryset = queryset.filter(**{'u.username__icontains': self.data.get('user_name')})
        if self.data.get("source_type"):
            queryset = queryset.filter(**{'rm.source_type__in': self.data.get('source_type')})
        if self.data.get('workspace_ids') is not None and len(self.data.get('workspace_ids')) > 0:
            workspace_ids = json.loads(self.data.get('workspace_ids'))
            queryset = queryset.filter(**{'workspace_id__in': workspace_ids})

        return queryset

    @staticmethod
    def is_x_pack_ee():
        workspace_model = DatabaseModelManage.get_model("workspace_model")
        return workspace_model is not None

    def page(self, current_page, page_size):
        is_x_pack_ee = self.is_x_pack_ee()
        return native_page_search(current_page, page_size, self.get_query_set(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage",
                         'sql', 'list_resource_mapping_ee.sql' if is_x_pack_ee else 'list_resource_mapping.sql')),
                                  with_table_name=False)

    def get_resource_count(self, result_list):
        """
        获取资源映射计数
        """
        if not result_list:
            return result_list
        is_paginated = isinstance(result_list, Page)

        data_to_process = result_list.get('records') if is_paginated else result_list

        if isinstance(data_to_process, list) and data_to_process:
            # 提取ID列表，确保每个项目都是字典且包含'id'键
            ids = [item['id'] for item in data_to_process
                   if isinstance(item, dict) and 'id' in item and item['id']]

            if ids:  # 只有在ids非空时才执行查询
                mapping_counts = ResourceMapping.objects.filter(
                    target_id__in=ids
                ).values('target_id').annotate(
                    count=models.Count('id')
                )

                # 构建目标ID到计数的映射
                count_dict = {str(item['target_id']): item['count'] for item in mapping_counts}

                # 为每个结果项添加资源计数
                for model in data_to_process:
                    if isinstance(model, dict) and 'id' in model:
                        model_id = str(model['id'])
                        model['resource_count'] = count_dict.get(model_id, 0)

        return result_list
