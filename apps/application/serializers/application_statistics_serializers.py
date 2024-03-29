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
from typing import List, Dict

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
    start_time = serializers.DateField(format='%Y-%m-%d', error_messages=ErrMessage.date("开始时间"))
    end_time = serializers.DateField(format='%Y-%m-%d', error_messages=ErrMessage.date("结束时间"))

    def get_end_time(self):
        return datetime.datetime.combine(
            datetime.datetime.strptime(self.data.get('end_time'), '%Y-%m-%d'),
            datetime.datetime.max.time())

    def get_start_time(self):
        return self.data.get('start_time')

    def get_customer_count(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return native_search(
            QuerySet(ApplicationPublicAccessClient).filter(application_id=self.data.get('application_id'),
                                                           create_time__gte=start_time,
                                                           create_time__lte=end_time),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count.sql')),
            with_search_one=True)

    def get_customer_count_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return native_search(
            {'default_sql': QuerySet(ApplicationPublicAccessClient).filter(
                application_id=self.data.get('application_id'),
                create_time__gte=start_time,
                create_time__lte=end_time)},
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count_trend.sql')))

    def get_chat_record_aggregate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        chat_record_aggregate = native_search(
            QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.UUIDField(),
                 'application_chat_record.create_time': models.DateTimeField()})).filter(
                **{'application_chat.application_id': self.data.get('application_id'),
                   'application_chat_record.create_time__gte': start_time,
                   'application_chat_record.create_time__lte': end_time}
            ),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'chat_record_count.sql')),
            with_search_one=True)
        customer = self.get_customer_count(with_valid=False)
        return {**chat_record_aggregate, **customer}

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
