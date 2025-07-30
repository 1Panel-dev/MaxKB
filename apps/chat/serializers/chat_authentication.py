# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： ChatAuthentication.py
    @date：2025/6/6 13:48
    @desc:
"""
import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken, ChatUserType, Application, ApplicationVersion
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
                token_details = signing.loads(token[7:])
        except Exception as e:
            pass
        if with_valid:
            self.is_valid(raise_exception=True)
        access_token = self.data.get("access_token")
        application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
        if application_access_token is not None and application_access_token.is_active:
            chat_user_id = token_details.get('chat_user_id') or str(uuid.uuid7())
            _type = AuthenticationType.CHAT_ANONYMOUS_USER
            return ChatUserToken(application_access_token.application_id, None, access_token, _type,
                                 ChatUserType.ANONYMOUS_USER,
                                 chat_user_id, ChatAuthentication(None)).to_token()
        else:
            raise NotFound404(404, _("Invalid access_token"))


class AuthProfileSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, label=_("access_token"))

    def profile(self):
        self.is_valid(raise_exception=True)
        access_token = self.data.get("access_token")
        application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
        if application_access_token is None:
            raise NotFound404(404, _("Invalid access_token"))
        if not application_access_token.is_active:
            raise NotFound404(404, _("Invalid access_token"))
        application_id = application_access_token.application_id
        profile = {
            'authentication': False
        }
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        chat_platform = DatabaseModelManage.get_model('chat_platform')
        if application_setting_model and chat_platform:
            application_setting = QuerySet(application_setting_model).filter(application_id=application_id).first()
            types = QuerySet(chat_platform).filter(is_active=True, is_valid=True).values_list('auth_type', flat=True)
            login_value = application_access_token.authentication_value.get('login_value', [])
            final_login_value = list(set(login_value) & set(types))
            if 'LOCAL' in login_value:
                final_login_value.insert(0, 'LOCAL')
            if application_setting is not None:
                profile = {
                    'icon': application_setting.application.icon,
                    'application_name': application_setting.application.name,
                    'bg_icon': application_setting.chat_background,
                    'authentication': application_access_token.authentication,
                    'authentication_type': application_access_token.authentication_value.get(
                        'type', 'password'),
                    'login_value': final_login_value
                }
        return profile


class ApplicationProfileSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    @staticmethod
    def reset_application(application, application_version):
        update_field_dict = {
            'application_name': 'name', 'desc': 'desc', 'prologue': 'prologue', 'dialogue_number': 'dialogue_number',
            'user_id': 'user_id', 'model_id': 'model_id', 'knowledge_setting': 'knowledge_setting',
            'model_setting': 'model_setting', 'model_params_setting': 'model_params_setting',
            'tts_model_params_setting': 'tts_model_params_setting',
            'problem_optimization': 'problem_optimization', 'work_flow': 'work_flow',
            'problem_optimization_prompt': 'problem_optimization_prompt', 'tts_model_id': 'tts_model_id',
            'stt_model_id': 'stt_model_id', 'tts_model_enable': 'tts_model_enable',
            'stt_model_enable': 'stt_model_enable', 'tts_type': 'tts_type',
            'tts_autoplay': 'tts_autoplay', 'stt_autosend': 'stt_autosend', 'file_upload_enable': 'file_upload_enable',
            'file_upload_setting': 'file_upload_setting'
        }
        for (version_field, app_field) in update_field_dict.items():
            _v = getattr(application_version, version_field)
            setattr(application, app_field, _v)

    def profile(self, with_valid=True):
        if with_valid:
            self.is_valid()
        application_id = self.data.get("application_id")
        application = QuerySet(Application).get(id=application_id)
        application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application.id).first()
        if application_access_token is None:
            raise AppUnauthorizedFailed(500, _("Illegal User"))
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        application_version = QuerySet(ApplicationVersion).filter(application_id=application.id).order_by(
            '-create_time').first()
        if application_version is not None:
            self.reset_application(application, application_version)
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
                                            'float_location': application_setting.float_location,
                                            'chat_background': application_setting.chat_background}
        base_node = [node for node in ((application.work_flow or {}).get('nodes', []) or []) if
                     node.get('id') == 'base-node']
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
                'work_flow': {'nodes': base_node} if base_node else None,
                'show_source': application_access_token.show_source,
                'show_exec': application_access_token.show_exec,
                'language': application_access_token.language,
                **application_setting_dict}
