# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_embed_serializers.py
    @date：2025/5/30 14:34
    @desc:
"""
import os
import uuid_utils.compat as uuid

from django.db.models import QuerySet
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken
from common.database_model_manage.database_model_manage import DatabaseModelManage
from maxkb.conf import PROJECT_DIR
from maxkb.const import CONFIG


class ChatEmbedSerializer(serializers.Serializer):
    host = serializers.CharField(required=True, label=_("Host"))
    protocol = serializers.CharField(required=True, label=_("protocol"))
    token = serializers.CharField(required=True, label=_("token"))

    def get_embed(self, with_valid=True, params=None):
        if params is None:
            params = {}
        if with_valid:
            self.is_valid(raise_exception=True)
        index_path = os.path.join(PROJECT_DIR, 'apps', "chat", 'template', 'embed.js')
        file = open(index_path, "r", encoding='utf-8')
        content = file.read()
        file.close()
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            access_token=self.data.get('token')).first()
        is_draggable = 'false'
        show_guide = 'true'
        float_icon = f"{self.data.get('protocol')}://{self.data.get('host')}{CONFIG.get_chat_path()}/MaxKB.gif"
        is_license_valid = DatabaseModelManage.get_model('license_is_valid')
        X_PACK_LICENSE_IS_VALID = is_license_valid() if is_license_valid is not None else False
        # 获取接入的query参数
        query = self.get_query_api_input(application_access_token.application, params)
        float_location = {"x": {"type": "right", "value": 0}, "y": {"type": "bottom", "value": 30}}
        header_font_color = "rgb(100, 106, 115)"
        application_setting_model = DatabaseModelManage.get_model('application_setting')
        if application_setting_model is not None and X_PACK_LICENSE_IS_VALID:
            application_setting = QuerySet(application_setting_model).filter(
                application_id=application_access_token.application_id).first()
            if application_setting is not None:
                is_draggable = 'true' if application_setting.draggable else 'false'
                if application_setting.float_icon is not None and len(application_setting.float_icon) > 0:
                    float_icon = application_setting.float_icon[1:] if application_setting.float_icon.startswith(
                        '.') else application_setting.float_icon
                    float_icon = f"{self.data.get('protocol')}://{self.data.get('host')}{CONFIG.get_chat_path()}{float_icon}"
                show_guide = 'true' if application_setting.show_guide else 'false'
                if application_setting.float_location is not None:
                    float_location = application_setting.float_location
                if application_setting.custom_theme is not None and len(
                        application_setting.custom_theme.get('header_font_color', 'rgb(100, 106, 115)')) > 0:
                    header_font_color = application_setting.custom_theme.get('header_font_color',
                                                                             'rgb(100, 106, 115)')

        is_auth = 'true' if application_access_token is not None and application_access_token.is_active else 'false'
        t = Template(content)
        s = t.render(
            Context(
                {'is_auth': is_auth, 'protocol': self.data.get('protocol'), 'host': self.data.get('host'),
                 'token': self.data.get('token'),
                 'white_list_str': ",".join(
                     application_access_token.white_list if application_access_token.white_list is not None else []),
                 'white_active': 'true' if application_access_token.white_active else 'false',
                 'is_draggable': is_draggable,
                 'float_icon': float_icon,
                 'prefix': CONFIG.get_chat_path(),
                 'query': query,
                 'show_guide': show_guide,
                 'x_type': float_location.get('x', {}).get('type', 'right'),
                 'x_value': float_location.get('x', {}).get('value', 0),
                 'y_type': float_location.get('y', {}).get('type', 'bottom'),
                 'y_value': float_location.get('y', {}).get('value', 30),
                 'max_kb_id': str(uuid.uuid7()).replace('-', ''),
                 'header_font_color': header_font_color}))
        response = HttpResponse(s, status=200, headers={'Content-Type': 'text/javascript'})
        return response

    @staticmethod
    def get_query_api_input(application, params):
        query = ''
        if application.work_flow is not None:
            work_flow = application.work_flow
            if work_flow is not None:
                for node in work_flow.get('nodes', []):
                    if node['id'] == 'base-node':
                        input_field_list = node.get('properties', {}).get('api_input_field_list',
                                                                          node.get('properties', {}).get(
                                                                              'input_field_list', []))
                        if input_field_list is not None:
                            for field in input_field_list:
                                if field['assignment_method'] == 'api_input' and field['variable'] in params:
                                    query += f"&{field['variable']}={params[field['variable']]}"
        if 'asker' in params:
            query += f"&asker={params.get('asker')}"
        return query
