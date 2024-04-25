# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  公共访问连接认证
"""
from django.db.models import QuerySet

from application.models.api_key_model import ApplicationAccessToken
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import RoleConstants, Permission, Group, Operate, Auth
from common.exception.app_exception import AppAuthenticationFailed


class PublicAccessToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        token_details = get_token_details()
        if token_details is None:
            return False
        return (
                'application_id' in token_details and
                'access_token' in token_details and
                token_details.get('type') == AuthenticationType.APPLICATION_ACCESS_TOKEN.value)

    def handle(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=auth_details.get('application_id')).first()
        if application_access_token is None:
            raise AppAuthenticationFailed(1002, "身份验证信息不正确")
        if not application_access_token.is_active:
            raise AppAuthenticationFailed(1002, "身份验证信息不正确")
        if not application_access_token.access_token == auth_details.get('access_token'):
            raise AppAuthenticationFailed(1002, "身份验证信息不正确")

        return application_access_token.application.user, Auth(
            role_list=[RoleConstants.APPLICATION_ACCESS_TOKEN],
            permission_list=[
                Permission(group=Group.APPLICATION,
                           operate=Operate.USE,
                           dynamic_tag=str(
                               application_access_token.application_id))],
            application_id=application_access_token.application_id,
            client_id=auth_details.get('client_id'),
            client_type=AuthenticationType.APPLICATION_ACCESS_TOKEN.value,
            current_role=RoleConstants.APPLICATION_ACCESS_TOKEN
        )
