# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： application_version_api.py
    @date：2024/10/15 17:18
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class ApplicationVersionApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'work_flow', 'create_time', 'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Primary key id"),
                                     description=_("Primary key id")),
                'name': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Version Name"),
                                       description=_("Version Name")),
                'work_flow': openapi.Schema(type=openapi.TYPE_STRING, title=_("Workflow data"),
                                            description=_('Workflow data')),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Creation time"),
                                              description=_('Creation time')),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Modification time"),
                                              description=_('Modification time'))
            }
        )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),
                    openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('Version Name'))]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),
                    openapi.Parameter(name='work_flow_version_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application version id')), ]

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Version Name"),
                                           description=_("Version Name"))
                }
            )
