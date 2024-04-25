# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  应用api key认证
"""
from django.db.models import QuerySet

from application.models.api_key_model import ApplicationApiKey
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Permission, Group, Operate, RoleConstants, Auth
from common.exception.app_exception import AppAuthenticationFailed


class ApplicationKey(AuthBaseHandle):
    def handle(self, request, token: str, get_token_details):
        application_api_key = QuerySet(ApplicationApiKey).filter(secret_key=token).first()
        if application_api_key is None:
            raise AppAuthenticationFailed(500, "secret_key 无效")
        if not application_api_key.is_active:
            raise AppAuthenticationFailed(500, "secret_key 无效")
        permission_list = [Permission(group=Group.APPLICATION,
                                      operate=Operate.USE,
                                      dynamic_tag=str(
                                          application_api_key.application_id)),
                           Permission(group=Group.APPLICATION,
                                      operate=Operate.MANAGE,
                                      dynamic_tag=str(
                                          application_api_key.application_id))
                           ]
        return application_api_key.user, Auth(role_list=[RoleConstants.APPLICATION_KEY],
                                              permission_list=permission_list,
                                              application_id=application_api_key.application_id,
                                              client_id=str(application_api_key.id),
                                              client_type=AuthenticationType.API_KEY.value,
                                              current_role=RoleConstants.APPLICATION_KEY
                                              )

    def support(self, request, token: str, get_token_details):
        return str(token).startswith("application-")
