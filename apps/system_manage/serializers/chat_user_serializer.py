import json

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken, ChatUserType
from common.auth.common import ChatUserToken, ChatAuthentication
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.exception.app_exception import AppApiException
from common.log.log import record_log
from common.utils.common import password_encrypt
from common.utils.common import password_verify, needs_password_upgrade
from common.utils.rsa_util import decrypt
from system_manage.models import ResourceChatUserGroupAuthorize, ResourceType, \
    UserGroupRelation, ResourceChatUserAuthorize, ChatUser
from users.serializers.login import LoginRequest

system_version, system_get_key = Cache_Version.SYSTEM.value


class ChatUserAccessTokenSerializer(serializers.Serializer):

    @staticmethod
    def create_token_and_cache(access_token, user, request):
        status = 500  # 默认失败状态
        workspace_id = 'default'
        try:
            application_access_token = ApplicationAccessToken.objects.filter(
                access_token=access_token
            ).first()

            if not application_access_token:
                raise AppApiException(1005, _('Invalid access token'))

            application_id = application_access_token.application_id
            workspace_id = application_access_token.application.workspace_id
            # 检查用户是否有权限访问该应用
            is_authorized = ResourceChatUserAuthorize.objects.filter(
                resource_id=application_id,
                resource_type=ResourceType.APPLICATION.value,
                is_auth=True,
                user_id=user.id
            ).exists()
            if not is_authorized:
                # 获取资源组授权的用户组ID
                resource_group_ids = ResourceChatUserGroupAuthorize.objects.filter(
                    resource_id=application_id,
                    resource_type=ResourceType.APPLICATION.value,
                    is_auth=True,
                ).values_list('user_group_id', flat=True)

                # 如果有资源组授权，则检查用户是否属于这些用户组
                if resource_group_ids.exists():
                    is_authorized = UserGroupRelation.objects.filter(
                        user_id=user.id,
                        group_id__in=resource_group_ids
                    ).exists()

            if not is_authorized:
                raise AppApiException(1005, _('The user does not have permission to access the application'))
            token = ChatUserToken(
                application_id, user.id, access_token, AuthenticationType.CHAT_USER,
                ChatUserType.CHAT_USER, user.id, ChatAuthentication(user.source)
            ).to_token()
            status = 200
            return token
        finally:
            record_log(
                menu='Chat User/login',
                operate='Log in',
                request=request,
                user={'username': user.username},
                status=status,
                operation_object={'name': user.username},
                workspace_id=workspace_id
            )

    @staticmethod
    def get_auth_setting(access_token):
        auth_setting = {}
        application_access_token = ApplicationAccessToken.objects.filter(
            access_token=access_token
        ).first()

        if not application_access_token:
            raise AppApiException(1005, _('Invalid access token'))
        if application_access_token:
            auth_setting = application_access_token.authentication_value

        return auth_setting

    @staticmethod
    def local_login(instance, access_token):
        username = instance.get("username", "")
        encryptedData = instance.get("encryptedData", "")
        if encryptedData:
            json_data = json.loads(decrypt(encryptedData))
            instance.update(json_data)
        try:
            LoginRequest(data=instance).is_valid(raise_exception=True)
        except Exception as e:
            raise e
        auth_setting = ChatUserAccessTokenSerializer.get_auth_setting(access_token)

        max_attempts = auth_setting.get("max_attempts", 1)
        password = instance.get("password")
        captcha = instance.get("captcha", "")

        # 判断是否需要验证码
        need_captcha = True
        if max_attempts == -1:
            need_captcha = False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f'chat_{username}'), version=system_version) or 0
            need_captcha = fail_count >= max_attempts

        if need_captcha:
            if not captcha:
                raise AppApiException(1005, _("Captcha is required"))

            captcha_cache = cache.get(
                Cache_Version.CAPTCHA.get_key(captcha=f"chat_{username}"),
                version=Cache_Version.CAPTCHA.get_version()
            )
            if captcha_cache is None or captcha.lower() != captcha_cache:
                raise AppApiException(1005, _("Captcha code error or expiration"))

        user = ChatUser.objects.filter(username=username).first()

        if not user or not password_verify(password, user.password):
            record_login_fail(username)
            raise AppApiException(500, _('The username or password is incorrect'))

        if needs_password_upgrade(user.password):
            user.password = password_encrypt(password)
            user.save(update_fields=['password'])
        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
        cache.delete(system_get_key(f'chat_{username}'), version=system_version)
        return user


def record_login_fail(username: str, expire: int = 600):
    """记录登录失败次数"""
    if not username:
        return
    fail_key = system_get_key(f'chat_{username}')
    fail_count = cache.get(fail_key, version=system_version)
    if fail_count is None:
        cache.set(fail_key, 1, timeout=expire, version=system_version)
    else:
        cache.incr(fail_key, 1, version=system_version)
