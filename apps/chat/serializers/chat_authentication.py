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

from application.models import ApplicationAccessToken, ChatUserType, Application, ApplicationTypeChoices, \
    WorkFlowVersion
from application.serializers.application import ApplicationSerializerModel
from common.auth.common import ChatUserToken, ChatAuthentication
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import NotFound404, AppUnauthorizedFailed


class AnonymousAuthenticationSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, label=_("access_token"))

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
        if application_access_token is not None and application_access_token.is_active:
            chat_user_id = token_details.get('chat_user_id') or str(uuid.uuid1())
            _type = AuthenticationType.CHAT_ANONYMOUS_USER
            return ChatUserToken(application_access_token.application_id, None, access_token, _type,
                                 ChatUserType.ANONYMOUS_USER,
                                 chat_user_id, ChatAuthentication(None, False, False)).to_token()
        else:
            raise NotFound404(404, _("Invalid access_token"))


class AuthProfileSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, label=_("access_token"))

    def profile(self):
        self.is_valid(raise_exception=True)
        access_token = self.data.get("access_token")
        application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
        application_id = application_access_token.application_id
        profile = {
            'authentication': False
        }
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        if application_setting_model:
            application_setting = QuerySet(application_setting_model).filter(application_id=application_id).first()
            profile = {
                'icon': application_setting.application.icon,
                'application_name': application_setting.application.name,
                'bg_icon': application_setting.chat_background,
                'authentication': application_setting.authentication,
                'authentication_type': application_setting.authentication_value.get(
                    'type', 'password'),
                'login_value': application_setting.authentication_value.get('login_value', [])
            }
        return profile


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
