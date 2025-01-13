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
from common.exception.app_exception import AppAuthenticationFailed, ChatException
from common.models.db_model_manage import DBModelManage
from common.util.common import password_encrypt
from django.utils.translation import gettext_lazy as _

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
        if request.path != '/api/application/profile':
            application_setting_model = DBModelManage.get_model('application_setting')
            xpack_cache = DBModelManage.get_model('xpack_cache')
            X_PACK_LICENSE_IS_VALID = False if xpack_cache is None else xpack_cache.get('XPACK_LICENSE_IS_VALID', False)
            if application_setting_model is not None and X_PACK_LICENSE_IS_VALID:
                application_setting = QuerySet(application_setting_model).filter(application_id=str(
                    application_access_token.application_id)).first()
                if application_setting.authentication:
                    authentication = auth_details.get('authentication', {})
                    if authentication is None:
                        authentication = {}
                    if application_setting.authentication_value.get('type') != authentication.get(
                            'type') or password_encrypt(
                        application_setting.authentication_value.get('value')) != authentication.get('value'):
                        raise ChatException(1002, _('Authentication information is incorrect'))
        if application_access_token is None:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        if not application_access_token.is_active:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        if not application_access_token.access_token == auth_details.get('access_token'):
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))

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
