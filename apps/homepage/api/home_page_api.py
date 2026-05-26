# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： home_page_api.py
    @date：2026/5/18 16:02
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    inline_serializer,
)
from rest_framework import serializers

from application.api.application_stats import ApplicationStatsResult
from common.mixins.api_mixin import APIMixin


class ApplicationMonitoringAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="workspace_id",
            description="工作空间id",
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        ),
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return ApplicationStatsResult


class RankingBaseAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
            OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="Name",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="current_page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Current page"),
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Page size"),
            ),
        ]


class RankingBaseExportAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
            OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="Name",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]


class ApplicationTokensRankingAPI(RankingBaseAPI):

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ApplicationTokensRankingResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="ApplicationTokensRankingPage",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total count")),
                        "records": serializers.ListField(
                            help_text=_("Application tokens ranking list"),
                            child=inline_serializer(
                                name="ApplicationTokensRankingItem",
                                fields={
                                    "application_id": serializers.CharField(help_text=_("Application ID")),
                                    "application_name": serializers.CharField(help_text=_("Application name")),
                                    "total_tokens": serializers.IntegerField(help_text=_("Total consumed tokens")),
                                },
                            ),
                        ),
                    },
                ),
            },
        )


class ApplicationQuestionRankingAPI(RankingBaseAPI):

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ApplicationQuestionRankingResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="ApplicationQuestionRankingPage",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total count")),
                        "records": serializers.ListField(
                            help_text=_("Application question ranking list"),
                            child=inline_serializer(
                                name="ApplicationQuestionRankingItem",
                                fields={
                                    "application_id": serializers.CharField(help_text=_("Application ID")),
                                    "application_name": serializers.CharField(help_text=_("Application name")),
                                    "chat_record_count": serializers.IntegerField(help_text=_("Question count")),
                                },
                            ),
                        ),
                    },
                ),
            },
        )


class UserTokensRankingAPI(RankingBaseAPI):

    @staticmethod
    def get_response(serializer=inline_serializer(name="UserTokensRankingResponse", fields={
        "code": serializers.IntegerField(help_text=_("Response code")),
        "message": serializers.CharField(help_text=_("Response message")),
        "data": inline_serializer(name="UserTokensRankingPage",
                                  fields={"total": serializers.IntegerField(help_text=_("Total count")),
                                          "records": serializers.ListField(help_text=_("User tokens ranking list"),
                                                                           child=inline_serializer(
                                                                               name="UserTokensRankingItem", fields={
                                                                                   "chat_user_id": serializers.CharField(
                                                                                       help_text=_("Chat user ID")),
                                                                                   "chat_user_type": serializers.CharField(
                                                                                       help_text=_("Chat user type")),
                                                                                   "total_tokens": serializers.IntegerField(
                                                                                       help_text=_(
                                                                                           "Total consumed tokens")),
                                                                                   "chat_record_count": serializers.IntegerField(
                                                                                       help_text=_("Question count")),
                                                                                   "asker": serializers.JSONField(
                                                                                       help_text=_(
                                                                                           "Asker user information")), }, ), ), }, ), }, )):
        return serializer


class ApplicationAggregationAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ApplicationAggregationResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="ApplicationAggregationData",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total application count")),
                        "published": serializers.IntegerField(help_text=_("Published application count")),
                        "unpublished": serializers.IntegerField(help_text=_("Unpublished application count")),
                    },
                ),
            },
        )

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
        ]


class TokensAggregationAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
            OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]


class KnowledgeAggregationAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return inline_serializer(
            name="KnowledgeAggregationResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="KnowledgeAggregationData",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total knowledge count")),
                        "document_count": serializers.IntegerField(help_text=_("Total document count")),
                        "failed_document_count": serializers.IntegerField(help_text=_("Failed document count")),
                    },
                ),
            },
        )

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
        ]


class ToolAggregationAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ToolAggregationResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="ToolAggregationData",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total tool count")),
                        "active": serializers.IntegerField(help_text=_("Active tool count")),
                        "inactive": serializers.IntegerField(help_text=_("Inactive tool count")),
                    },
                ),
            },
        )

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
        ]


class ModelAggregationAPI(APIMixin):

    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ModelAggregationResponse",
            fields={
                "code": serializers.IntegerField(help_text=_("Response code")),
                "message": serializers.CharField(help_text=_("Response message")),
                "data": inline_serializer(
                    name="ModelAggregationData",
                    fields={
                        "total": serializers.IntegerField(help_text=_("Total model count")),
                        "active": serializers.IntegerField(help_text=_("Active model count")),
                        "inactive": serializers.IntegerField(help_text=_("Inactive model count")),
                    },
                ),
            },
        )

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=_("Workspace ID"),
            ),
        ]
