# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： homepage.py
    @date：2026/5/13 14:34
    @desc:
"""
import datetime
import os
from typing import List, Dict

from django.db import models
from django.db.models import QuerySet, Count, Q, UUIDField, Sum, F, BigIntegerField, Value, ExpressionWrapper, \
    IntegerField, OuterRef, Subquery, JSONField
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, ApplicationChatUserStats, Chat, ChatRecord
from common.constants.permission_constants import RoleConstants
from common.db.search import native_search, get_dynamics_model, page_search
from common.utils.common import get_file_content
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelTypeConst
from models_provider.models import Model
from system_manage.models import WorkspaceUserResourcePermission
from tools.models import Tool, ToolType


def hasPermission(auth, permission):
    if 'USER' in auth.role_list:
        return True
    if permission in auth.permission_list:
        return True
    return False


def is_workspace_manage(auth, workspace_id):
    return RoleConstants.WORKSPACE_MANAGE.value.__str__() + ":/WORKSPACE/" + workspace_id in auth.role_list


def get_format_time(date_time):
    d = datetime.datetime.strptime(date_time, '%Y-%m-%d').date()
    naive = datetime.datetime.combine(d, datetime.time.min)
    return timezone.make_aware(naive, timezone.get_default_timezone())


class HomePageSerializer(serializers.Serializer):
    class TokensAggregation(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_("Workspace ID"))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
        end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

        def aggregation(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            data = self.data
            user_id = data["user_id"]
            workspace_id = data.get("workspace_id")
            start_time = get_format_time(data["start_time"])
            end_time = get_format_time(data["end_time"])
            workspace_manage = is_workspace_manage(auth, workspace_id)
            query = ChatRecord.objects.filter(
                create_time__gte=start_time,
                create_time__lte=end_time,
            )
            if workspace_manage:
                query = query.filter(
                    chat__application__workspace_id=workspace_id
                )
            else:
                permission_list = (
                    ["VIEW", "MANAGE", "ROLE"]
                    if hasPermission(auth, "APPLICATION:READ")
                    else ["VIEW", "MANAGE"]
                )
                permission_subquery = (
                    WorkspaceUserResourcePermission.objects
                    .filter(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        auth_type="APPLICATION",
                        permission_list__overlap=permission_list
                    )
                    .annotate(
                        target_uuid=Cast(
                            "target",
                            output_field=UUIDField()
                        )
                    )
                    .values("target_uuid")
                )
                query = query.filter(
                    chat__application_id__in=permission_subquery
                )

            return query.aggregate(
                total_tokens=Coalesce(
                    Sum(
                        F("message_tokens") + F("answer_tokens"),
                        output_field=IntegerField()
                    ),
                    0
                )
            )["total_tokens"]

    class ApplicationUserTokenRanking(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_("Workspace ID"))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
        end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

        def ranking(self, auth, current_page, page_size, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)

            workspace_id = self.validated_data.get("workspace_id")
            user_id = self.validated_data.get("user_id")
            start_time = get_format_time(self.data.get("start_time"))
            end_time = get_format_time(self.data.get("end_time"))
            base_queryset = Chat.objects.filter(
                is_deleted=False,
                chat_user_id__isnull=False,
                create_time__gte=start_time,
                create_time__lte=end_time
            ).exclude(
                chat_user_id=""
            )

            workspace_manage = is_workspace_manage(auth, workspace_id)
            if workspace_manage:
                base_queryset = base_queryset.filter(
                    application__workspace_id=workspace_id
                )
            else:
                permission_list = (
                    ["VIEW", "MANAGE", "ROLE"]
                    if hasPermission(auth, "APPLICATION:READ")
                    else ["VIEW", "MANAGE"]
                )

                application_id_queryset = QuerySet(WorkspaceUserResourcePermission).filter(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    auth_type="APPLICATION",
                    permission_list__overlap=permission_list,
                ).annotate(
                    target_uuid=Cast("target", output_field=UUIDField())
                ).values_list(
                    "target_uuid",
                    flat=True
                )

                base_queryset = base_queryset.filter(
                    application_id__in=application_id_queryset
                )

            token_expr = ExpressionWrapper(
                F("chatrecord__message_tokens") + F("chatrecord__answer_tokens"),
                output_field=BigIntegerField()
            )

            latest_asker_queryset = base_queryset.filter(
                chat_user_id=OuterRef("chat_user_id"),
                chat_user_type=OuterRef("chat_user_type"),
            ).order_by(
                "-create_time"
            ).values(
                "asker"
            )[:1]

            queryset = base_queryset.values(
                "chat_user_id",
                "chat_user_type",
            ).annotate(
                total_tokens=Coalesce(
                    Sum(token_expr),
                    Value(0),
                    output_field=BigIntegerField()
                ),
                chat_record_count=Count(
                    "chatrecord__id",
                    distinct=True
                ),
                asker=Subquery(
                    latest_asker_queryset,
                    output_field=JSONField()
                )
            ).order_by(
                "-total_tokens"
            )

            return page_search(
                current_page,
                page_size,
                queryset,
                lambda item: {
                    "chat_user_id": item["chat_user_id"],
                    "chat_user_type": item["chat_user_type"],
                    "asker": item["asker"],
                    "total_tokens": item["total_tokens"],
                    "chat_record_count": item["chat_record_count"],
                }
            )

    class ApplicationQuestionRanking(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
        end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

        def ranking(self, auth, current_page, page_size, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)

            workspace_id = self.validated_data.get("workspace_id")
            user_id = self.validated_data.get("user_id")
            queryset = Application.objects.filter(workspace_id=workspace_id)
            start_time = get_format_time(self.data.get("start_time"))
            end_time = get_format_time(self.data.get("end_time"))
            queryset = queryset.filter(
                create_time__gte=start_time,
                create_time__lte=end_time)
            workspace_manage = is_workspace_manage(auth, workspace_id)
            if not workspace_manage:
                permission_list = (
                    ["VIEW", "MANAGE", "ROLE"]
                    if hasPermission(auth, "APPLICATION:READ")
                    else ["VIEW", "MANAGE"]
                )

                queryset = queryset.filter(
                    id__in=QuerySet(WorkspaceUserResourcePermission)
                    .filter(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        auth_type="APPLICATION",
                        permission_list__overlap=permission_list,
                    )
                    .annotate(
                        target_uuid=Cast("target", output_field=UUIDField())
                    )
                    .values_list("target_uuid", flat=True)
                )

            queryset = queryset.annotate(
                # 问题数 / 对话轮次数量
                chat_record_count_total=Coalesce(
                    Sum(
                        "chat__chat_record_count",
                        filter=Q(chat__is_deleted=False),
                    ),
                    Value(0),
                    output_field=BigIntegerField(),
                ),

                # 对话用户数量，按 chat_user_id 去重
                chat_user_count=Count(
                    "chat__chat_user_id",
                    filter=(
                            Q(chat__is_deleted=False)
                            & Q(chat__chat_user_id__isnull=False)
                            & ~Q(chat__chat_user_id="")
                    ),
                    distinct=True,
                ),
            ).order_by(
                "-chat_record_count_total"
            )

            return page_search(
                current_page,
                page_size,
                queryset,
                lambda a: {
                    "id": a.id,
                    "name": a.name,
                    "chat_record_count": a.chat_record_count_total,
                    "chat_user_count": a.chat_user_count,
                },
            )

    class ApplicationTokensRanking(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
        end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

        def ranking(self, auth, current_page, page_size, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            start_time = get_format_time(self.data.get('start_time'))
            end_time = get_format_time(self.data.get('end_time'))
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")

            token_expr = ExpressionWrapper(
                F("chat__chatrecord__message_tokens") + F("chat__chatrecord__answer_tokens"),
                output_field=BigIntegerField()
            )

            queryset = Application.objects.filter(
                create_time__gte=start_time,
                create_time__lte=end_time)

            workspace_manage = is_workspace_manage(auth, workspace_id)

            if workspace_manage:
                queryset = queryset.filter(workspace_id=workspace_id)
            else:
                permission_list = ["VIEW", "MANAGE", "ROLE"] if hasPermission(
                    auth,
                    "APPLICATION:READ"
                ) else ["VIEW", "MANAGE"]

                queryset = queryset.filter(
                    id__in=QuerySet(WorkspaceUserResourcePermission)
                    .filter(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        auth_type="APPLICATION",
                        permission_list__overlap=permission_list
                    )
                    .annotate(target_uuid=Cast("target", output_field=UUIDField()))
                    .values_list("target_uuid", flat=True)
                )

            queryset = queryset.annotate(
                total_tokens=Coalesce(
                    Sum(
                        token_expr,
                        filter=Q(chat__is_deleted=False)
                    ),
                    Value(0),
                    output_field=BigIntegerField()
                ),
                chat_record_count_total=Count(
                    "chat__chatrecord__id",
                    filter=Q(chat__is_deleted=False),
                    output_field=IntegerField()
                )
            ).order_by("-total_tokens")

            return page_search(
                current_page,
                page_size,
                queryset,
                lambda a: {
                    "id": a.id,
                    "name": a.name,
                    "total_tokens": a.total_tokens,
                    "chat_record_count": a.chat_record_count_total,
                }
            )

    class ApplicationMonitoring(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        application_id = serializers.UUIDField(required=False, allow_null=True, label=_("Application ID"))
        start_time = serializers.DateField(format='%Y-%m-%d', label=_("Start time"))
        end_time = serializers.DateField(format='%Y-%m-%d', label=_("End time"))

        def get_customer_count_trend(self, application_queryset, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            start_time = get_format_time(self.data.get("start_time"))
            end_time = get_format_time(self.data.get("end_time"))
            query_set = QuerySet(ApplicationChatUserStats).filter(
                create_time__gte=start_time,
                create_time__lte=end_time)
            application_id = self.data.get('application_id')
            if application_id:
                query_set.filter(application_id=application_id)
            else:
                query_set.filter(application_id__in=application_queryset)
            return native_search(
                {'default_sql': query_set},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'customer_count_trend.sql')))

        def get_chat_record_aggregate_trend(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            workspace_id = self.data.get("workspace_id")
            start_time = get_format_time(self.data.get("start_time"))
            end_time = get_format_time(self.data.get("end_time"))
            application_id = self.data.get('application_id')
            applicationSerializer = HomePageSerializer.Application(
                data={"user_id": user_id, 'workspace_id': workspace_id})
            applicationSerializer.is_valid(raise_exception=True)
            application_query_set = applicationSerializer.get_aggregation_query_set(
                auth)
            chat_record_aggregate_trend = native_search(
                {'default_sql': QuerySet(model=get_dynamics_model(
                    {'application_chat.application_id': models.UUIDField(),
                     'application_chat_record.create_time': models.DateTimeField()})).filter(
                    **{**({'application_chat.application_id': application_id} if application_id else {
                        'application_chat.application_id__in': application_query_set}),
                       'application_chat_record.create_time__gte': start_time,
                       'application_chat_record.create_time__lte': end_time}
                )},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'chat_record_count_trend.sql')))
            customer_count_trend = self.get_customer_count_trend(application_query_set, with_valid=False)
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

    class Application(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))

        def get_aggregation_query_set(self, auth):
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")
            workspace_manage = is_workspace_manage(auth, workspace_id)
            if workspace_manage:
                return QuerySet(Application).filter(workspace_id=workspace_id)
            permission_list = ["VIEW", "MANAGE", "ROLE"] if hasPermission(auth, "APPLICATION:READ") else ['VIEW',
                                                                                                          'MANAGE']
            return QuerySet(Application).filter(
                id__in=QuerySet(WorkspaceUserResourcePermission)
                .filter(workspace_id=workspace_id,
                        user_id=user_id,
                        auth_type="APPLICATION",
                        permission_list__overlap=permission_list
                        ).annotate(target_uuid=Cast("target", output_field=UUIDField()))
                .values_list("target_uuid", flat=True))

        def aggregation(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_aggregation_query_set(auth)
            result = query_set.aggregate(
                total=Count("id"),
                publish_count=Count("id", filter=Q(is_publish=True)),
                un_publish_count=Count("id", filter=Q(is_publish=False)),
            )
            return {
                "total": result["total"],
                "publish_count": result["publish_count"],
                "un_publish_count": result["un_publish_count"],
            }

    class Knowledge(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))

        def get_aggregation_query_set(self, auth):
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")
            if is_workspace_manage(auth, workspace_id):
                return QuerySet(Knowledge).filter(workspace_id=workspace_id)
            permission_list = ["VIEW", "MANAGE", "ROLE"] if hasPermission(auth, "APPLICATION:READ") else ['VIEW',
                                                                                                          'MANAGE']
            return QuerySet(Knowledge).filter(
                id__in=QuerySet(WorkspaceUserResourcePermission).filter(workspace_id=workspace_id,
                                                                        user_id=user_id,
                                                                        auth_type="KNOWLEDGE",
                                                                        permission_list__overlap=permission_list
                                                                        ).annotate(
                    target_uuid=Cast("target", output_field=UUIDField()))
                .values_list("target_uuid", flat=True))

        def aggregation(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_aggregation_query_set(auth)
            result = query_set.aggregate(
                total=Count("id", distinct=True),
                document_count=Count(
                    "document",
                    distinct=True,
                ),
                failure_count=Count(
                    "document",
                    filter=Q(
                        document__status__contains="3",
                    ),
                    distinct=True,
                ),
            )
            return {
                "total": result["total"] or 0,
                "document_count": result["document_count"] or 0,
                "failure_count": result["failure_count"] or 0,
            }

    class Tool(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))

        def get_aggregation_query_set(self, auth):
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")
            if is_workspace_manage(auth, workspace_id):
                return QuerySet(Tool).filter(workspace_id=workspace_id)
            permission_list = ["VIEW", "MANAGE", "ROLE"] if hasPermission(auth, "APPLICATION:READ") else ['VIEW',
                                                                                                          'MANAGE']
            return QuerySet(Tool).filter(
                id__in=QuerySet(WorkspaceUserResourcePermission).filter(workspace_id=workspace_id,
                                                                        user_id=user_id,
                                                                        auth_type="TOOL",
                                                                        permission_list__overlap=permission_list
                                                                        ).annotate(
                    target_uuid=Cast("target", output_field=UUIDField()))
                .values_list("target_uuid", flat=True))

        def aggregation(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_aggregation_query_set(auth)
            result = query_set.aggregate(
                total=Count("id"),
                custom_count=Count("id", filter=Q(tool_type=ToolType.CUSTOM)),
                skill_count=Count("id", filter=Q(tool_type=ToolType.SKILL)),
                mcp_count=Count("id", filter=Q(tool_type=ToolType.MCP)),
                workflow_count=Count("id", filter=Q(tool_type=ToolType.WORKFLOW)),
                data_source_count=Count("id", filter=Q(tool_type=ToolType.DATA_SOURCE)),
            )
            return {
                "total": result["total"] or 0,
                "custom_count": result["custom_count"] or 0,
                "skill_count": result["skill_count"] or 0,
                "mcp_count": result["mcp_count"] or 0,
                "workflow_count": result["workflow_count"] or 0,
                "data_source_count": result["data_source_count"] or 0,
            }

    class Model(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))

        def get_aggregation_query_set(self, auth):
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")
            if is_workspace_manage(auth, workspace_id):
                return QuerySet(Model).filter(workspace_id=workspace_id)
            permission_list = ["VIEW", "MANAGE", "ROLE"] if hasPermission(auth, "APPLICATION:READ") else ['VIEW',
                                                                                                          'MANAGE']
            return QuerySet(Model).filter(
                id__in=QuerySet(WorkspaceUserResourcePermission).filter(workspace_id=workspace_id,
                                                                        user_id=user_id,
                                                                        auth_type="MODEL",
                                                                        permission_list__overlap=permission_list
                                                                        ).annotate(
                    target_uuid=Cast("target", output_field=UUIDField()))
                .values_list("target_uuid", flat=True))

        def aggregation(self, auth, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_aggregation_query_set(auth)
            result = query_set.aggregate(
                total=Count("id"),
                embedding_count=Count("id", filter=Q(model_type=ModelTypeConst.EMBEDDING.name)),
                llm_count=Count("id", filter=Q(model_type=ModelTypeConst.LLM.name)),
            )
            total = result["total"] or 0
            embedding_count = result["embedding_count"] or 0
            llm_count = result["llm_count"] or 0
            return {
                "total": total,
                "embedding_count": embedding_count,
                "llm_count": llm_count
            }
