# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： application_version_views.py
    @date：2024/10/15 16:49
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.application_version_serializers import ApplicationVersionSerializer
from application.swagger_api.application_version_api import ApplicationVersionApi
from application.views import get_application_operation_object
from common.auth import has_permissions, TokenAuth
from common.constants.permission_constants import PermissionConstants, CompareConstants, ViewPermission, RoleConstants, \
    Permission, Group, Operate
from common.log.log import log
from common.response import result
from django.utils.translation import gettext_lazy as _


class ApplicationVersionView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_("Get the application list"),
                         operation_id=_("Get the application list"),
                         manual_parameters=ApplicationVersionApi.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ApplicationVersionApi.get_response_body_api()),
                         tags=[_('Application/Version')])
    @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
    def get(self, request: Request, application_id: str):
        return result.success(
            ApplicationVersionSerializer.Query(
                data={'name': request.query_params.get('name'), 'user_id': request.user.id,
                      'application_id': application_id}).list())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the list of application versions by page"),
                             operation_id=_("Get the list of application versions by page"),
                             manual_parameters=result.get_page_request_params(
                                 ApplicationVersionApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ApplicationVersionApi.get_response_body_api()),
                             tags=[_('Application/Version')])
        @has_permissions(PermissionConstants.APPLICATION_READ,
                         ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                        [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                                        dynamic_tag=keywords.get('application_id'))],
                                        compare=CompareConstants.AND), compare=CompareConstants.AND)
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(
                ApplicationVersionSerializer.Query(
                    data={'name': request.query_params.get('name'), 'user_id': request.user,
                          'application_id': application_id}).page(
                    current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get application version details"),
                             operation_id=_("Get application version details"),
                             manual_parameters=ApplicationVersionApi.Operate.get_request_params_api(),
                             responses=result.get_api_response(ApplicationVersionApi.get_response_body_api()),
                             tags=[_('Application/Version')])
        @has_permissions(PermissionConstants.APPLICATION_READ, ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                                              [lambda r, keywords: Permission(
                                                                                  group=Group.APPLICATION,
                                                                                  operate=Operate.USE,
                                                                                  dynamic_tag=keywords.get(
                                                                                      'application_id'))],
                                                                              compare=CompareConstants.AND),
                         compare=CompareConstants.AND)
        def get(self, request: Request, application_id: str, work_flow_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'user_id': request.user,
                          'application_id': application_id, 'work_flow_version_id': work_flow_version_id}).one())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Modify application version information"),
                             operation_id=_("Modify application version information"),
                             manual_parameters=ApplicationVersionApi.Operate.get_request_params_api(),
                             request_body=ApplicationVersionApi.Edit.get_request_body_api(),
                             responses=result.get_api_response(ApplicationVersionApi.get_response_body_api()),
                             tags=[_('Application/Version')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="Modify application version information",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str, work_flow_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'application_id': application_id, 'work_flow_version_id': work_flow_version_id,
                          'user_id': request.user.id}).edit(
                    request.data))
