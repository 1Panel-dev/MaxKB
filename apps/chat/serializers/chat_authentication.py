# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： ChatAuthentication.py
    @date：2025/6/6 13:48
    @desc:
"""
import uuid

from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken, ClientType, Application, ApplicationTypeChoices, WorkFlowVersion
from application.serializers.application import ApplicationSerializerModel
from common.auth.common import ChatUserToken, ChatAuthentication

from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import NotFound404, AppApiException, AppUnauthorizedFailed


def auth(application_id, access_token, authentication_value, token_details):
    client_id = token_details.get('client_id')
    if client_id is None:
        client_id = str(uuid.uuid1())
    _type = AuthenticationType.CHAT_ANONYMOUS_USER
    if authentication_value is not None:
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        if application_setting_model is not None:
            application_setting = QuerySet(application_setting_model).filter(application_id=application_id).first()
            if application_setting.authentication:
                auth_type = application_setting.authentication_value.get('type')
                auth_value = authentication_value.get(auth_type + '_value')
                if auth_type == 'password':
                    if authentication_value.get('type') == 'password':
                        if auth_value == authentication_value.get(auth_type + '_value'):
                            return ChatUserToken(application_id, None, access_token, _type, ClientType.ANONYMOUS_USER,
                                                 client_id, ChatAuthentication(auth_type, True, True))
                    else:
                        raise AppApiException(500, '认证方式不匹配')
    return ChatUserToken(application_id, None, access_token, _type, ClientType.ANONYMOUS_USER,
                         client_id, ChatAuthentication(None, False, False))


class AuthenticationSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, label=_("access_token"))
    authentication_value = serializers.JSONField(required=False, allow_null=True,
                                                 label=_("Certification Information"))

    def auth(self, request, with_valid=True):
        token = request.META.get('HTTP_AUTHORIZATION')
        token_details = {}
        try:
            # 校验token
            if token is not None:
                token_details = signing.loads(token)
        except Exception as e:
            pass
        if with_valid:
            self.is_valid(raise_exception=True)
        access_token = self.data.get("access_token")
        application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
        authentication_value = self.data.get('authentication_value', None)
        if application_access_token is not None and application_access_token.is_active:
            chat_user_token = auth(application_access_token.application_id, access_token, authentication_value,
                                   token_details)

            return chat_user_token.to_token()
        else:
            raise NotFound404(404, _("Invalid access_token"))


class ApplicationProfileSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    def profile(self, with_valid=True):
        if with_valid:
            self.is_valid()
        application_id = self.data.get("application_id")
        application = QuerySet(Application).get(id=application_id)
        application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application.id).first()
        if application_access_token is None:
            raise AppUnauthorizedFailed(500, _("Illegal User"))
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        if application.type == ApplicationTypeChoices.WORK_FLOW:
            work_flow_version = QuerySet(WorkFlowVersion).filter(application_id=application.id).order_by(
                '-create_time')[0:1].first()
            if work_flow_version is not None:
                application.work_flow = work_flow_version.work_flow

        license_is_valid = cache.get(Cache_Version.SYSTEM.get_key(key='license_is_valid'),
                                     version=Cache_Version.SYSTEM.get_version())
        application_setting_dict = {}
        if application_setting_model is not None and license_is_valid:
            application_setting = QuerySet(application_setting_model).filter(
                application_id=application_access_token.application_id).first()
            if application_setting is not None:
                custom_theme = getattr(application_setting, 'custom_theme', {})
                float_location = getattr(application_setting, 'float_location', {})
                if not custom_theme:
                    application_setting.custom_theme = {
                        'theme_color': '',
                        'header_font_color': ''
                    }
                if not float_location:
                    application_setting.float_location = {
                        'x': {'type': '', 'value': ''},
                        'y': {'type': '', 'value': ''}
                    }
                application_setting_dict = {'show_source': application_access_token.show_source,
                                            'show_history': application_setting.show_history,
                                            'draggable': application_setting.draggable,
                                            'show_guide': application_setting.show_guide,
                                            'avatar': application_setting.avatar,
                                            'show_avatar': application_setting.show_avatar,
                                            'float_icon': application_setting.float_icon,
                                            'authentication': application_setting.authentication,
                                            'authentication_type': application_setting.authentication_value.get(
                                                'type', 'password'),
                                            'login_value': application_setting.authentication_value.get(
                                                'login_value', []),
                                            'disclaimer': application_setting.disclaimer,
                                            'disclaimer_value': application_setting.disclaimer_value,
                                            'custom_theme': application_setting.custom_theme,
                                            'user_avatar': application_setting.user_avatar,
                                            'show_user_avatar': application_setting.show_user_avatar,
                                            'float_location': application_setting.float_location}
        return {**ApplicationSerializerModel(application).data,
                'stt_model_id': application.stt_model_id,
                'tts_model_id': application.tts_model_id,
                'stt_model_enable': application.stt_model_enable,
                'tts_model_enable': application.tts_model_enable,
                'tts_type': application.tts_type,
                'tts_autoplay': application.tts_autoplay,
                'stt_autosend': application.stt_autosend,
                'file_upload_enable': application.file_upload_enable,
                'file_upload_setting': application.file_upload_setting,
                'work_flow': {'nodes': [node for node in ((application.work_flow or {}).get('nodes', []) or []) if
                                        node.get('id') == 'base-node']},
                'show_source': application_access_token.show_source,
                'language': application_access_token.language,
                **application_setting_dict}
