# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_statistics_serializers.py
    @date：2024/3/27 10:55
    @desc:
"""
import datetime
import os

from django.db import models
from django.db.models.query import QuerySet
from rest_framework import serializers

from application.models.api_key_model import ApplicationPublicAccessClient
from common.db.search import native_search, get_dynamics_model
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from smartdoc.conf import PROJECT_DIR


class ApplicationStatisticsSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("应用id"))
    history_day = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("历史天数"))

    def get_end_time(self):
        history_day = self.data.get('history_day')
        return datetime.datetime.now() - datetime.timedelta(days=history_day)

    def get_customer_count(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_search(
            QuerySet(ApplicationPublicAccessClient).filter(application_id=self.data.get('application_id'),
                                                           create_time__gte=self.get_end_time()),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count.sql')),
            with_search_one=True)

    def get_customer_count_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_search(
            {'default_sql': QuerySet(ApplicationPublicAccessClient).filter(
                application_id=self.data.get('application_id'),
                create_time__gte=self.get_end_time())},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count_trend.sql')))

    def get_chat_record_aggregate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_search(
            QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': self.get_end_time()}
            ),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'chat_record_count.sql')),
            with_search_one=True)

    def get_chat_record_aggregate_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_search(
            {'default_sql': QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': self.get_end_time()}
            )},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'chat_record_count_trend.sql')))
