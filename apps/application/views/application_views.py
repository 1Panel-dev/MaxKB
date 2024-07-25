# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_views.py
    @date：2023/10/27 14:56
    @desc:
"""

from django.core import cache
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.application_serializers import ApplicationSerializer
from application.serializers.application_statistics_serializers import ApplicationStatisticsSerializer
from application.swagger_api.application_api import ApplicationApi
from application.swagger_api.application_statistics_api import ApplicationStatisticsApi
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import CompareConstants, PermissionConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.exception.app_exception import AppAuthenticationFailed
from common.response import result
from common.swagger_api.common_api import CommonApi
from common.util.common import query_params_to_single_dict
from dataset.serializers.dataset_serializers import DataSetSerializers

chat_cache = cache.caches['chat_cache']


class ApplicationStatistics(APIView):
    class CustomerCount(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="用户统计",
                             operation_id="用户统计",
                             tags=["应用/统计"],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_response(
                                 ApplicationStatisticsApi.CustomerCount.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_customer_count())

    class CustomerCountTrend(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="用户统计趋势",
                             operation_id="用户统计趋势",
                             tags=["应用/统计"],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 ApplicationStatisticsApi.CustomerCountTrend.get_response_body_api()))
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_customer_count_trend())

    class ChatRecordAggregate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="对话相关统计",
                             operation_id="对话相关统计",
                             tags=["应用/统计"],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_response(
                                 ApplicationStatisticsApi.ChatRecordAggregate.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_chat_record_aggregate())

    class ChatRecordAggregateTrend(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="对话相关统计趋势",
                             operation_id="对话相关统计趋势",
                             tags=["应用/统计"],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 ApplicationStatisticsApi.ChatRecordAggregate.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_chat_record_aggregate_trend())


class Application(APIView):
    authentication_classes = [TokenAuth]

    class EditIcon(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="修改应用icon",
                             operation_id="修改应用icon",
                             tags=['应用'],
                             manual_parameters=ApplicationApi.EditApplicationIcon.get_request_params_api(),
                             request_body=ApplicationApi.Operate.get_request_body_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND), PermissionConstants.APPLICATION_EDIT,
            compare=CompareConstants.AND)
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.IconOperate(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'image': request.FILES.get('file')}).edit(request.data))

    class Embed(APIView):
        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="获取嵌入js",
                             operation_id="获取嵌入js",
                             tags=["应用"],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api())
        def get(self, request: Request):
            return ApplicationSerializer.Embed(
                data={'protocol': request.query_params.get('protocol'), 'token': request.query_params.get('token'),
                      'host': request.query_params.get('host'), }).get_embed()

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary="获取模型列表",
                             operation_id="获取模型列表",
                             tags=["应用"],
                             manual_parameters=ApplicationApi.Model.get_request_params_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id,
                          'user_id': request.user.id}).list_model(request.query_params.get('model_type')))

    class Profile(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取应用相关信息",
                             operation_id="获取应用相关信息",
                             tags=["应用/会话"])
        def get(self, request: Request):
            if 'application_id' in request.auth.keywords:
                return result.success(ApplicationSerializer.Operate(
                    data={'application_id': request.auth.keywords.get('application_id'),
                          'user_id': request.user.id}).profile())
            raise AppAuthenticationFailed(401, "身份异常")

    class ApplicationKey(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="新增ApiKey",
                             operation_id="新增ApiKey",
                             tags=['应用/API_KEY'],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def post(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.ApplicationKeySerializer(
                    data={'application_id': application_id, 'user_id': request.user.id}).generate())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取应用API_KEY列表",
                             operation_id="获取应用API_KEY列表",
                             tags=['应用/API_KEY'],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api()
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.ApplicationKeySerializer(
                data={'application_id': application_id, 'user_id': request.user.id}).list())

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary="修改应用API_KEY",
                                 operation_id="修改应用API_KEY",
                                 tags=['应用/API_KEY'],
                                 manual_parameters=ApplicationApi.ApiKey.Operate.get_request_params_api(),
                                 request_body=ApplicationApi.ApiKey.Operate.get_request_body_api())
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND), PermissionConstants.APPLICATION_EDIT,
                compare=CompareConstants.AND)
            def put(self, request: Request, application_id: str, api_key_id: str):
                return result.success(
                    ApplicationSerializer.ApplicationKeySerializer.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'api_key_id': api_key_id}).edit(request.data))

            @action(methods=['DELETE'], detail=False)
            @swagger_auto_schema(operation_summary="删除应用API_KEY",
                                 operation_id="删除应用API_KEY",
                                 tags=['应用/API_KEY'],
                                 manual_parameters=ApplicationApi.ApiKey.Operate.get_request_params_api())
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND), PermissionConstants.APPLICATION_DELETE,
                compare=CompareConstants.AND)
            def delete(self, request: Request, application_id: str, api_key_id: str):
                return result.success(
                    ApplicationSerializer.ApplicationKeySerializer.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'api_key_id': api_key_id}).delete())

    class AccessToken(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="修改 应用AccessToken",
                             operation_id="修改 应用AccessToken",
                             tags=['应用/公开访问'],
                             manual_parameters=ApplicationApi.AccessToken.get_request_params_api(),
                             request_body=ApplicationApi.AccessToken.get_request_body_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.AccessTokenSerializer(data={'application_id': application_id}).edit(request.data))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取应用 AccessToken信息",
                             operation_id="获取应用 AccessToken信息",
                             manual_parameters=ApplicationApi.AccessToken.get_request_params_api(),
                             tags=['应用/公开访问'],
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.AccessTokenSerializer(data={'application_id': application_id}).one())

    class Authentication(APIView):
        @action(methods=['OPTIONS'], detail=False)
        def options(self, request, *args, **kwargs):
            return HttpResponse(headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                                         "Access-Control-Allow-Methods": "POST",
                                         "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}, )

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="应用认证",
                             operation_id="应用认证",
                             request_body=ApplicationApi.Authentication.get_request_body_api(),
                             tags=["应用/认证"],
                             security=[])
        def post(self, request: Request):
            return result.success(
                ApplicationSerializer.Authentication(data={'access_token': request.data.get("access_token")}).auth(
                    request),
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                         "Access-Control-Allow-Methods": "POST",
                         "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}
            )

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建应用",
                         operation_id="创建应用",
                         request_body=ApplicationApi.Create.get_request_body_api(),
                         tags=['应用'])
    @has_permissions(PermissionConstants.APPLICATION_CREATE, compare=CompareConstants.AND)
    def post(self, request: Request):
        return result.success(ApplicationSerializer.Create(data={'user_id': request.user.id}).insert(request.data))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取应用列表",
                         operation_id="获取应用列表",
                         manual_parameters=ApplicationApi.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                         tags=['应用'])
    @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        return result.success(
            ApplicationSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).list())

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="命中测试列表", operation_id="命中测试列表",
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=["应用"])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
             RoleConstants.APPLICATION_KEY],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.HitTest(data={'id': application_id, 'user_id': request.user.id,
                                                    "query_text": request.query_params.get("query_text"),
                                                    "top_number": request.query_params.get("top_number"),
                                                    'similarity': request.query_params.get('similarity'),
                                                    'search_mode': request.query_params.get('search_mode')}).hit_test(
                ))

    class Publish(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="发布应用",
                             operation_id="发布应用",
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             request_body=ApplicationApi.Publish.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=['应用'])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id, 'user_id': request.user.id}).publish(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="删除应用",
                             operation_id="删除应用",
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=['应用'])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND),
            lambda r, k: Permission(group=Group.APPLICATION, operate=Operate.DELETE,
                                    dynamic_tag=k.get('application_id')), compare=CompareConstants.AND)
        def delete(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).delete(
                with_valid=True))

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="修改应用",
                             operation_id="修改应用",
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             request_body=ApplicationApi.Edit.get_request_body_api(),
                             responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                             tags=['应用'])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(data={'application_id': application_id, 'user_id': request.user.id}).edit(
                    request.data))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取应用详情",
                             operation_id="获取应用详情",
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                             tags=['应用'])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
             RoleConstants.APPLICATION_KEY],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).one())

    class ListApplicationDataSet(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取当前应用可使用的知识库",
                             operation_id="获取当前应用可使用的知识库",
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=['应用'])
        @has_permissions(ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                        [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                                        dynamic_tag=keywords.get('application_id'))],
                                        compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).list_dataset())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="分页获取应用列表",
                             operation_id="分页获取应用列表",
                             manual_parameters=result.get_page_request_params(
                                 ApplicationApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ApplicationApi.get_response_body_api()),
                             tags=['应用'])
        @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                ApplicationSerializer.Query(
                    data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).page(
                    current_page, page_size))
