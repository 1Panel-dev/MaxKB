# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_stats.py
    @date：2025/6/9 20:34
    @desc:
"""
import datetime
import os
from typing import Dict, List

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers

from application.models import ApplicationChatUserStats, Application
from common.db.search import native_search, get_dynamics_model
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from maxkb.settings import edition


class ApplicationStatsSerializer(serializers.Serializer):
    chat_record_count = serializers.IntegerField(required=True, label=_("Number of conversations"))
    customer_added_count = serializers.IntegerField(required=True, label=_("Number of new users"))
    customer_num = serializers.IntegerField(required=True, label=_("Total number of users"))
    day = serializers.CharField(required=True, label=_("date"))
    star_num = serializers.IntegerField(required=True, label=_("Number of Likes"))
    tokens_num = serializers.IntegerField(required=True, label=_("Tokens consumption"))
    trample_num = serializers.IntegerField(required=True, label=_("Number of thumbs-downs"))


class ApplicationStatisticsSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
    end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def get_end_time(self):
        d = datetime.datetime.strptime(self.data.get('end_time'), '%Y-%m-%d').date()
        naive = datetime.datetime.combine(d, datetime.time.max)
        return timezone.make_aware(naive, timezone.get_default_timezone())

    def get_start_time(self):
        d = datetime.datetime.strptime(self.data.get('start_time'), '%Y-%m-%d').date()
        naive = datetime.datetime.combine(d, datetime.time.min)
        return timezone.make_aware(naive, timezone.get_default_timezone())

    def get_customer_count_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return native_search(
            {'default_sql': QuerySet(ApplicationChatUserStats).filter(
                application_id=self.data.get('application_id'),
                create_time__gte=start_time,
                create_time__lte=end_time)},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count_trend.sql')))

    def get_chat_record_aggregate_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        chat_record_aggregate_trend = native_search(
            {'default_sql': QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': start_time,
                   'application_chat_record.create_time__lte': end_time}
            )},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'chat_record_count_trend.sql')))
        customer_count_trend = self.get_customer_count_trend(with_valid=False)
        return self.merge_customer_chat_record(chat_record_aggregate_trend, customer_count_trend)

    def merge_customer_chat_record(self, chat_record_aggregate_trend: List[Dict], customer_count_trend: List[Dict]):

        return [{**self.find(chat_record_aggregate_trend, lambda c: c.get('day').strftime('%Y-%m-%d') == day,
                             {'star_num': 0, 'trample_num': 0, 'tokens_num': 0, 'chat_record_count': 0,
                              'customer_num': 0,
                              'day': day}),
                 **self.find(customer_count_trend, lambda c: c.get('day').strftime('%Y-%m-%d') == day,
                             {'customer_added_count': 0})}
                for
                day in
                self.get_days_between_dates(self.data.get('start_time'), self.data.get('end_time'))]

    @staticmethod
    def find(source_list, condition, default):
        value_list = [row for row in source_list if condition(row)]
        if len(value_list) > 0:
            return value_list[0]
        return default

    @staticmethod
    def get_days_between_dates(start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
        return days

    def get_token_usage_statistics(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        get_token_usage = native_search(
            {'default_sql': QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': start_time,
                   'application_chat_record.create_time__lte': end_time}
            )},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                             ('get_token_usage_ee.sql' if ['PE', 'EE'].__contains__(
                                 edition) else 'get_token_usage.sql'))))
        return get_token_usage

    def get_top_questions_statistics(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        get_top_questions = native_search(
            {'default_sql': QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': start_time,
                   'application_chat_record.create_time__lte': end_time}
            )},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', (
                    'top_questions_ee.sql' if ['PE', 'EE'].__contains__(edition) else 'top_questions.sql'))))
        return get_top_questions
