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

import openpyxl
from django.db import models
from django.db.models import QuerySet, Sum, Count, F, Q, BigIntegerField, IntegerField, Value, Window
from django.db.models.functions import RowNumber, Coalesce
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _, gettext
from django.utils import timezone
from rest_framework import serializers

from application.models import ApplicationChatUserStats, Application, Chat, ChatRecord
from common.db.search import native_search, get_dynamics_model, page_search
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
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("User Name"))
    start_time = serializers.DateField(format="%Y-%m-%d", label=_("Start time"))
    end_time = serializers.DateField(format="%Y-%m-%d", label=_("End time"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        query_set = QuerySet(Application).filter(id=self.data.get("application_id"))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _("Application id does not exist"))

    def get_end_time(self):
        d = datetime.datetime.strptime(self.data.get("end_time"), "%Y-%m-%d").date()
        naive = datetime.datetime.combine(d, datetime.time.max)
        return timezone.make_aware(naive, timezone.get_default_timezone())

    def get_start_time(self):
        d = datetime.datetime.strptime(self.data.get("start_time"), "%Y-%m-%d").date()
        naive = datetime.datetime.combine(d, datetime.time.min)
        return timezone.make_aware(naive, timezone.get_default_timezone())

    def get_customer_count_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return native_search(
            {
                "default_sql": QuerySet(ApplicationChatUserStats).filter(
                    application_id=self.data.get("application_id"),
                    create_time__gte=start_time,
                    create_time__lte=end_time,
                )
            },
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", "sql", "customer_count_trend.sql")
            ),
        )

    def get_chat_record_aggregate_trend(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        chat_record_aggregate_trend = native_search(
            {
                "default_sql": QuerySet(
                    model=get_dynamics_model(
                        {
                            "application_chat.application_id": models.UUIDField(),
                            "application_chat_record.create_time": models.DateTimeField(),
                        }
                    )
                ).filter(
                    **{
                        "application_chat.application_id": self.data.get("application_id"),
                        "application_chat_record.create_time__gte": start_time,
                        "application_chat_record.create_time__lte": end_time,
                    }
                )
            },
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", "sql", "chat_record_count_trend.sql")
            ),
        )
        customer_count_trend = self.get_customer_count_trend(with_valid=False)
        return self.merge_customer_chat_record(chat_record_aggregate_trend, customer_count_trend)

    def merge_customer_chat_record(self, chat_record_aggregate_trend: List[Dict], customer_count_trend: List[Dict]):

        return [
            {
                **self.find(
                    chat_record_aggregate_trend,
                    lambda c: c.get("day").strftime("%Y-%m-%d") == day,
                    {
                        "star_num": 0,
                        "trample_num": 0,
                        "tokens_num": 0,
                        "chat_record_count": 0,
                        "customer_num": 0,
                        "day": day,
                    },
                ),
                **self.find(
                    customer_count_trend,
                    lambda c: c.get("day").strftime("%Y-%m-%d") == day,
                    {"customer_added_count": 0},
                ),
            }
            for day in self.get_days_between_dates(self.data.get("start_time"), self.data.get("end_time"))
        ]

    @staticmethod
    def find(source_list, condition, default):
        value_list = [row for row in source_list if condition(row)]
        if len(value_list) > 0:
            return value_list[0]
        return default

    @staticmethod
    def get_days_between_dates(start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date.strftime("%Y-%m-%d"))
            current_date += datetime.timedelta(days=1)
        return days

    def get_token_usage_statistics(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        get_token_usage = native_search(
            {
                "default_sql": QuerySet(
                    model=get_dynamics_model(
                        {
                            "application_chat.application_id": models.UUIDField(),
                            "application_chat_record.create_time": models.DateTimeField(),
                        }
                    )
                ).filter(
                    **{
                        "application_chat.application_id": self.data.get("application_id"),
                        "application_chat_record.create_time__gte": start_time,
                        "application_chat_record.create_time__lte": end_time,
                    }
                )
            },
            select_string=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "application",
                    "sql",
                    ("get_token_usage_ee.sql" if ["PE", "EE"].__contains__(edition) else "get_token_usage.sql"),
                )
            ),
        )
        return get_token_usage

    def get_top_questions_statistics(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        get_top_questions = native_search(
            {
                "default_sql": QuerySet(
                    model=get_dynamics_model(
                        {
                            "application_chat.application_id": models.UUIDField(),
                            "application_chat_record.create_time": models.DateTimeField(),
                        }
                    )
                ).filter(
                    **{
                        "application_chat.application_id": self.data.get("application_id"),
                        "application_chat_record.create_time__gte": start_time,
                        "application_chat_record.create_time__lte": end_time,
                    }
                )
            },
            select_string=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "application",
                    "sql",
                    ("top_questions_ee.sql" if ["PE", "EE"].__contains__(edition) else "top_questions.sql"),
                )
            ),
        )
        return get_top_questions

    def _get_chat_queryset(self):
        """当前智能体范围内未删除、带用户标识的对话。"""
        queryset = Chat.objects.filter(
            application_id=self.data.get("application_id"),
            is_deleted=False,
            chat_user_id__isnull=False,
        ).exclude(chat_user_id="")
        name = self.data.get("name")
        if name:
            queryset = queryset.filter(asker__username__contains=name)
        return queryset

    @staticmethod
    def _build_asker_map(base_queryset):
        """一次查询拿到每个 (chat_user_id, chat_user_type) 最新的 asker。"""
        latest_rows = (
            base_queryset.annotate(
                _rn=Window(
                    expression=RowNumber(),
                    partition_by=[F("chat_user_id"), F("chat_user_type")],
                    order_by=F("create_time").desc(),
                )
            )
            .filter(_rn=1)
            .values("chat_user_id", "chat_user_type", "asker")
        )
        return {(row["chat_user_id"], row["chat_user_type"]): row["asker"] for row in latest_rows}

    def _get_ranking_queryset(self, kind):
        """按用户统计当前智能体同期 Tokens / 对话次数，返回 (聚合 queryset, 基础 queryset)。"""
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        base_queryset = self._get_chat_queryset()
        record_time_filter = Q(
            chatrecord__create_time__gte=start_time,
            chatrecord__create_time__lte=end_time,
        )
        queryset = (
            base_queryset.filter(record_time_filter)
            .values("chat_user_id", "chat_user_type")
            .annotate(
                total_tokens=Coalesce(
                    Sum(F("chatrecord__message_tokens") + F("chatrecord__answer_tokens"), filter=record_time_filter),
                    Value(0),
                    output_field=BigIntegerField(),
                ),
                chat_record_count=Count("chatrecord__id", filter=record_time_filter, distinct=True),
            )
        )
        if kind == "questions":
            queryset = queryset.order_by("-chat_record_count", "chat_user_id")
        else:
            queryset = queryset.order_by("-total_tokens", "chat_user_id")
        return queryset, base_queryset

    def get_ranking_statistics(self, kind, current_page, page_size, with_valid=True):
        """分页查询当前智能体的用户排行，kind 为 userTokens / questions。"""
        if with_valid:
            self.is_valid(raise_exception=True)
        queryset, base_queryset = self._get_ranking_queryset(kind)
        asker_map = self._build_asker_map(base_queryset)
        return page_search(
            current_page,
            page_size,
            queryset,
            lambda item: {
                "chat_user_id": item["chat_user_id"],
                "chat_user_type": item["chat_user_type"],
                "asker": asker_map.get((item["chat_user_id"], item["chat_user_type"])),
                "total_tokens": item["total_tokens"],
                "chat_record_count": item["chat_record_count"],
            },
        )

    def get_tokens_aggregation(self, with_valid=True):
        """当前智能体同期 Tokens 总量，不受用户名搜索影响。"""
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return ChatRecord.objects.filter(
            chat__application_id=self.data.get("application_id"),
            chat__is_deleted=False,
            create_time__gte=start_time,
            create_time__lte=end_time,
        ).aggregate(
            total_tokens=Coalesce(Sum(F("message_tokens") + F("answer_tokens"), output_field=IntegerField()), Value(0))
        )["total_tokens"]

    def get_chat_record_aggregation(self, with_valid=True):
        """当前智能体同期对话次数，不受用户名搜索影响。"""
        if with_valid:
            self.is_valid(raise_exception=True)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return ChatRecord.objects.filter(
            chat__application_id=self.data.get("application_id"),
            chat__is_deleted=False,
            create_time__gte=start_time,
            create_time__lte=end_time,
        ).count()

    def export_ranking_statistics(self, kind, with_valid=True):
        """按当前筛选导出完整用户排行。"""
        if with_valid:
            self.is_valid(raise_exception=True)
        total = (
            self.get_tokens_aggregation(with_valid=False)
            if kind == "userTokens"
            else self.get_chat_record_aggregation(with_valid=False)
        )
        queryset, base_queryset = self._get_ranking_queryset(kind)
        asker_map = self._build_asker_map(base_queryset)
        workbook = openpyxl.Workbook(write_only=True)
        worksheet = workbook.create_sheet(title="Sheet1")
        headers = [
            gettext("ranking"),
            gettext("User Name"),
            gettext("Token consumption"),
            gettext("proportion"),
            gettext("number of questions"),
            gettext("Average tokens per request"),
        ]
        worksheet.append(headers)
        index = 0
        for item in queryset:
            index += 1
            user_info = asker_map.get((item["chat_user_id"], item["chat_user_type"])) or {}
            username = user_info.get("username", "")
            total_tokens = item.get("total_tokens", 0)
            chat_record_count = item.get("chat_record_count", 0)
            proportion = (
                (chat_record_count / total if total else 0)
                if kind == "questions"
                else (total_tokens / total if total else 0)
            )
            worksheet.append(
                [
                    index,
                    username,
                    total_tokens,
                    proportion,
                    chat_record_count,
                    total_tokens / chat_record_count if chat_record_count else 0,
                ]
            )
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="data.xlsx"'
        workbook.save(response)
        return response
