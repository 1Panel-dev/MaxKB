# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： application_version_serializers.py
    @date：2024/10/15 16:42
    @desc:
"""
from typing import Dict

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import WorkFlowVersion
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage


class ApplicationVersionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkFlowVersion
        fields = ['id', 'name', 'application_id', 'work_flow', 'publish_user_id', 'publish_user_name', 'create_time',
                  'update_time']


class ApplicationVersionEditSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=128, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_("Version Name")))


class ApplicationVersionSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_("Application ID")))
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char(_("summary")))

        def get_query_set(self):
            query_set = QuerySet(WorkFlowVersion).filter(application_id=self.data.get('application_id'))
            if 'name' in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(name__contains=self.data.get('name'))
            return query_set.order_by("-create_time")

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_query_set()
            return [ApplicationVersionModelSerializer(v).data for v in query_set]

        def page(self, current_page, page_size, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(current_page, page_size,
                               self.get_query_set(),
                               post_records_handler=lambda v: ApplicationVersionModelSerializer(v).data)

    class Operate(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_("Application ID")))
        work_flow_version_id = serializers.UUIDField(required=True,
                                                     error_messages=ErrMessage.uuid(_("Workflow version id")))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            work_flow_version = QuerySet(WorkFlowVersion).filter(application_id=self.data.get('application_id'),
                                                                 id=self.data.get('work_flow_version_id')).first()
            if work_flow_version is not None:
                return ApplicationVersionModelSerializer(work_flow_version).data
            else:
                raise AppApiException(500, _('Workflow version does not exist'))

        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ApplicationVersionEditSerializer(data=instance).is_valid(raise_exception=True)
            work_flow_version = QuerySet(WorkFlowVersion).filter(application_id=self.data.get('application_id'),
                                                                 id=self.data.get('work_flow_version_id')).first()
            if work_flow_version is not None:
                name = instance.get('name', None)
                if name is not None and len(name) > 0:
                    work_flow_version.name = name
                work_flow_version.save()
                return ApplicationVersionModelSerializer(work_flow_version).data
            else:
                raise AppApiException(500, _('Workflow version does not exist'))
