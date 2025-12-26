# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 17:17
    @desc:
"""
import os

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_page_search, get_dynamics_model
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR


class ResourceMappingSerializer(serializers.Serializer):
    resource = serializers.CharField(required=True, label=_('resource'))
    resource_id = serializers.UUIDField(required=True, label=_('resource Id'))
    resource_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('resource'))

    def get_query_set(self):
        queryset = QuerySet(model=get_dynamics_model({
            'name': models.CharField(),
            'target_id': models.CharField(),
            "target_type": models.CharField()
        }))

        queryset = queryset.filter(target_id=self.data.get('resource_id'),
                                   target_type=self.data.get('resource'))

        if self.data.get('resource_name'):
            queryset = queryset.filter(name__icontains=self.data.get('resource_name'))

        return queryset

    def page(self, current_page, page_size):
        return native_page_search(current_page, page_size, self.get_query_set(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage",
                         'sql', 'list_resource_mapping.sql')), with_table_name=False)
