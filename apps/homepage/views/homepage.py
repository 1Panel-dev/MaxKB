# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： homepage.py
@date：2026/5/13 16:40
@desc:
"""

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import AggregatePermission, ViewPermission
from homepage.api.home_page_api import (
    ApplicationTokensRankingAPI,
    ApplicationQuestionRankingAPI,
    UserTokensRankingAPI,
    ApplicationAggregationAPI,
    KnowledgeAggregationAPI,
    ToolAggregationAPI,
    ModelAggregationAPI,
    ApplicationMonitoringAPI,
    TokensAggregationAPI,
    RankingBaseExportAPI,
    system_parameters,
)
from homepage.serializers.homepage import HomePageSerializer, SystemHomePageSerializer
from django.utils.translation import gettext_lazy as _


class HomePageAPI(APIView):
    authentication_classes = [TokenAuth]

    class ChatRecordAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Chat record data aggregation"),
            summary=_("Chat record aggregation"),
            operation_id="homepage_chat_count_aggregation",
            parameters=TokensAggregationAPI.get_parameters(),
            responses=TokensAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.ChatRecordAggregation(
                    data={
                        "workspace_id": workspace_id,
                        "user_id": request.user.id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).aggregation(request.auth)
            )

    class TokensAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Tokens data aggregation"),
            summary=_("Tokens data aggregation"),
            operation_id="homepage_tokens_aggregation",
            parameters=TokensAggregationAPI.get_parameters(),
            responses=TokensAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.TokensAggregation(
                    data={
                        "workspace_id": workspace_id,
                        "user_id": request.user.id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).aggregation(request.auth)
            )

    class ApplicationTokensRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top applications by token consumption export"),
            summary=_("Top applications by token consumption export"),
            operation_id="homepage_application_tokens_ranking_export",
            parameters=RankingBaseExportAPI.get_parameters(),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_EXPORT.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return HomePageSerializer.ApplicationTokensRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": workspace_id,
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                    "name": request.query_params.get("name"),
                }
            ).export(request.auth)

    class ApplicationTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top applications by token consumption"),
            summary=_("Top applications by token consumption"),
            operation_id="homepage_application_tokens_ranking",
            parameters=ApplicationTokensRankingAPI.get_parameters(),
            responses=ApplicationTokensRankingAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(
                HomePageSerializer.ApplicationTokensRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                        "name": request.query_params.get("name"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class ApplicationQuestionRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top applications by question count export"),
            summary=_("Top applications by question count export"),
            operation_id="homepage_application_question_ranking_export",
            parameters=RankingBaseExportAPI.get_parameters(),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_EXPORT.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return HomePageSerializer.ApplicationQuestionRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": workspace_id,
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                    "name": request.query_params.get("name"),
                }
            ).export(request.auth)

    class ApplicationQuestionRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top applications by question count"),
            summary=_("Top applications by question count"),
            operation_id="homepage_application_question_ranking",
            parameters=ApplicationQuestionRankingAPI.get_parameters(),
            responses=ApplicationQuestionRankingAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(
                HomePageSerializer.ApplicationQuestionRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                        "name": request.query_params.get("name"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class UserTokensRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top users by token consumption export"),
            summary=_("Top users by token consumption export"),
            operation_id="homepage_user_tokens_ranking_export",
            parameters=RankingBaseExportAPI.get_parameters(),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_EXPORT.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return HomePageSerializer.ApplicationUserTokenRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": workspace_id,
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                    "name": request.query_params.get("name"),
                }
            ).export(request.auth)

    class UserTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top users by token consumption"),
            summary=_("Top users by token consumption"),
            operation_id="homepage_user_tokens_ranking",
            parameters=UserTokensRankingAPI.get_parameters(),
            responses=UserTokensRankingAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(
                HomePageSerializer.ApplicationUserTokenRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                        "name": request.query_params.get("name"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class ApplicationMonitoring(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Dialogue-related statistical trends"),
            summary=_("Dialogue-related statistical trends"),
            operation_id="Dialogue-related statistical trends",  # type: ignore
            parameters=ApplicationMonitoringAPI.get_parameters(),
            responses=ApplicationMonitoringAPI.get_response(),
            tags=[_("Home page")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.ApplicationMonitoring(
                    data={
                        "application_id": request.query_params.get("application_id"),
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).get_chat_record_aggregate_trend(request.auth)
            )

    class ApplicationAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Application data aggregation"),
            summary=_("Application data aggregation"),
            operation_id="homepage_application_aggregation",
            parameters=ApplicationAggregationAPI.get_parameters(),
            responses=ApplicationAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Application(
                    data={"workspace_id": workspace_id, "user_id": request.user.id}
                ).aggregation(request.auth)
            )

    class KnowledgeAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Knowledge data aggregation"),
            summary=_("Knowledge data aggregation"),
            operation_id="homepage_knowledge_aggregation",
            parameters=KnowledgeAggregationAPI.get_parameters(),
            responses=KnowledgeAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Knowledge(
                    data={"workspace_id": workspace_id, "user_id": request.user.id}
                ).aggregation(request.auth)
            )

    class ToolAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Tool data aggregation"),
            summary=_("Tool data aggregation"),
            operation_id="homepage_tool_aggregation",
            parameters=ToolAggregationAPI.get_parameters(),
            responses=ToolAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Tool(data={"workspace_id": workspace_id, "user_id": request.user.id}).aggregation(
                    request.auth
                )
            )

    class ModelAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Model data aggregation"),
            summary=_("Model data aggregation"),
            operation_id="homepage_model_aggregation",
            parameters=ModelAggregationAPI.get_parameters(),
            responses=ModelAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        @has_permissions(
            PermissionConstants.HOMEPAGE_READ.get_workspace_permission(),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Model(data={"workspace_id": workspace_id, "user_id": request.user.id}).aggregation(
                    request.auth
                )
            )


class SystemHomePageAPI(APIView):
    authentication_classes = [TokenAuth]

    class ApplicationAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide application data aggregation across all workspaces"),
            summary=_("System application aggregation"),
            operation_id="system_homepage_application_aggregation",
            parameters=system_parameters(ApplicationAggregationAPI),
            responses=ApplicationAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.Application(
                    data={"user_id": request.user.id, "workspace_id": request.query_params.get("workspace_id") or None}
                ).aggregation(request.auth)
            )

    class KnowledgeAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide knowledge data aggregation across all workspaces"),
            summary=_("System knowledge aggregation"),
            operation_id="system_homepage_knowledge_aggregation",
            parameters=system_parameters(KnowledgeAggregationAPI),
            responses=KnowledgeAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.Knowledge(
                    data={"user_id": request.user.id, "workspace_id": request.query_params.get("workspace_id") or None}
                ).aggregation(request.auth)
            )

    class ToolAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide tool data aggregation across all workspaces"),
            summary=_("System tool aggregation"),
            operation_id="system_homepage_tool_aggregation",
            parameters=system_parameters(ToolAggregationAPI),
            responses=ToolAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.Tool(
                    data={"user_id": request.user.id, "workspace_id": request.query_params.get("workspace_id") or None}
                ).aggregation(request.auth)
            )

    class ModelAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide model data aggregation across all workspaces"),
            summary=_("System model aggregation"),
            operation_id="system_homepage_model_aggregation",
            parameters=system_parameters(ModelAggregationAPI),
            responses=ModelAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.Model(
                    data={"user_id": request.user.id, "workspace_id": request.query_params.get("workspace_id") or None}
                ).aggregation(request.auth)
            )

    class TokensAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide tokens aggregation across all workspaces"),
            summary=_("System tokens aggregation"),
            operation_id="system_homepage_tokens_aggregation",
            parameters=system_parameters(TokensAggregationAPI),
            responses=TokensAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.TokensAggregation(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).aggregation(request.auth)
            )

    class ChatRecordAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide chat record aggregation across all workspaces"),
            summary=_("System chat record aggregation"),
            operation_id="system_homepage_chat_record_aggregation",
            parameters=system_parameters(TokensAggregationAPI),
            responses=TokensAggregationAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.ChatRecordAggregation(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).aggregation(request.auth)
            )

    class ApplicationTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top applications by token consumption across all workspaces"),
            summary=_("System application tokens ranking"),
            operation_id="system_homepage_application_tokens_ranking",
            parameters=system_parameters(ApplicationTokensRankingAPI),
            responses=ApplicationTokensRankingAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                SystemHomePageSerializer.ApplicationTokensRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "name": request.query_params.get("name"),
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class ApplicationQuestionRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top applications by question count across all workspaces"),
            summary=_("System application question ranking"),
            operation_id="system_homepage_application_question_ranking",
            parameters=system_parameters(ApplicationQuestionRankingAPI),
            responses=ApplicationQuestionRankingAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                SystemHomePageSerializer.ApplicationQuestionRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "name": request.query_params.get("name"),
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class UserTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top users by token consumption across all workspaces"),
            summary=_("System user tokens ranking"),
            operation_id="system_homepage_user_tokens_ranking",
            parameters=system_parameters(UserTokensRankingAPI),
            responses=UserTokensRankingAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                SystemHomePageSerializer.ApplicationUserTokenRanking(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "name": request.query_params.get("name"),
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).ranking(request.auth, current_page, page_size)
            )

    class UserTokensRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top users by token consumption export across all workspaces"),
            summary=_("System user tokens ranking export"),
            operation_id="system_homepage_user_tokens_ranking_export",
            parameters=system_parameters(RankingBaseExportAPI),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return SystemHomePageSerializer.ApplicationUserTokenRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": request.query_params.get("workspace_id") or None,
                    "name": request.query_params.get("name"),
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                }
            ).export(request.auth)

    class ApplicationQuestionRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top applications by question count export across all workspaces"),
            summary=_("System application question ranking export"),
            operation_id="system_homepage_application_question_ranking_export",
            parameters=system_parameters(RankingBaseExportAPI),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return SystemHomePageSerializer.ApplicationQuestionRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": request.query_params.get("workspace_id") or None,
                    "name": request.query_params.get("name"),
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                }
            ).export(request.auth)

    class ApplicationTokensRankingExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide top applications by token consumption export across all workspaces"),
            summary=_("System application tokens ranking export"),
            operation_id="system_homepage_application_tokens_ranking_export",
            parameters=system_parameters(RankingBaseExportAPI),
            responses=RankingBaseExportAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return SystemHomePageSerializer.ApplicationTokensRanking(
                data={
                    "user_id": request.user.id,
                    "workspace_id": request.query_params.get("workspace_id") or None,
                    "name": request.query_params.get("name"),
                    "start_time": request.query_params.get("start_time"),
                    "end_time": request.query_params.get("end_time"),
                }
            ).export(request.auth)

    class ApplicationMonitoring(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("System-wide dialogue monitoring trends across all workspaces"),
            summary=_("System application monitoring"),
            operation_id="system_homepage_application_monitoring",
            parameters=system_parameters(ApplicationMonitoringAPI),
            responses=ApplicationMonitoringAPI.get_response(),
            tags=[_("System home page")],
        )
        @has_permissions(
            RoleConstants.ADMIN,
            ViewPermission(
                roles=[RoleConstants.EXTENDS_ADMIN],
                permissions=[PermissionConstants.HOMEPAGE_READ.value],
                compare=CompareConstants.AND,
            ),
        )
        def get(self, request: Request):
            return result.success(
                SystemHomePageSerializer.ApplicationMonitoring(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": request.query_params.get("workspace_id") or None,
                        "application_id": request.query_params.get("application_id"),
                        "start_time": request.query_params.get("start_time"),
                        "end_time": request.query_params.get("end_time"),
                    }
                ).get_chat_record_aggregate_trend(request.auth)
            )
