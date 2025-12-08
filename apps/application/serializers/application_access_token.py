# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_access_token.py
    @date：2025/6/9 17:49
    @desc:
"""
import hashlib

import uuid_utils.compat as uuid
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken, Application
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException


class AccessTokenEditSerializer(serializers.Serializer):
    access_token_reset = serializers.BooleanField(required=False,
                                                  label=_("Reset Token"))
    is_active = serializers.BooleanField(required=False, label=_("Is it enabled"))
    access_num = serializers.IntegerField(required=False, max_value=10000000,
                                          min_value=0,
                                          label=_("Number of visits"))
    white_active = serializers.BooleanField(required=False,
                                            label=_("Whether to enable whitelist"))
    white_list = serializers.ListSerializer(required=False, child=serializers.CharField(required=True,
                                                                                        label=_("Whitelist")),
                                            label=_("Whitelist")),
    show_source = serializers.BooleanField(required=False,
                                           label=_("Whether to display knowledge sources"))
    show_exec = serializers.BooleanField(required=False,
                                         label=_("Display execution details"))
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                     label=_("language"))
    authentication = serializers.BooleanField(default=False, label="Do you need authentication")

    authentication_value = serializers.JSONField(required=False, label="Certified value", default=dict)


class AccessTokenSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def edit(self, instance):
        self.is_valid(raise_exception=True)
        AccessTokenEditSerializer(data=instance).is_valid(raise_exception=True)
        application_access_token = QuerySet(ApplicationAccessToken).get(
            application_id=self.data.get('application_id'))
        if 'is_active' in instance:
            application_access_token.is_active = instance.get("is_active")
        if 'access_token_reset' in instance and instance.get('access_token_reset'):
            application_access_token.access_token = hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()[8:24]
        if 'access_num' in instance and instance.get('access_num') is not None:
            application_access_token.access_num = instance.get("access_num")
        if 'white_active' in instance and instance.get('white_active') is not None:
            application_access_token.white_active = instance.get("white_active")
        if 'white_list' in instance and instance.get('white_list') is not None:
            application_access_token.white_list = instance.get('white_list')
        if 'show_source' in instance and instance.get('show_source') is not None:
            application_access_token.show_source = instance.get('show_source')
        if 'show_exec' in instance and instance.get('show_exec') is not None:
            application_access_token.show_exec = instance.get('show_exec')
        if 'language' in instance and instance.get('language') is not None:
            application_access_token.language = instance.get('language')
        if 'language' not in instance or instance.get('language') is None:
            application_access_token.language = None

        application_access_token.save()
        license_is_valid = cache.get(Cache_Version.SYSTEM.get_key(key='license_is_valid'),
                                     version=Cache_Version.SYSTEM.get_version())
        if license_is_valid:
            if instance.get('authentication') is not None and instance.get(
                    'authentication_value') is not None:
                application_access_token.authentication = instance.get('authentication')
                application_access_token.authentication_value = instance.get('authentication_value')
                application_access_token.save()
        return self.one(with_valid=False)

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=application_id).first()
        if application_access_token is None:
            application_access_token = ApplicationAccessToken(application_id=application_id,
                                                              access_token=hashlib.md5(
                                                                  str(uuid.uuid7()).encode()).hexdigest()[
                                                                           8:24], is_active=True)
            application_access_token.save()
        other = {}
        license_is_valid = cache.get(Cache_Version.SYSTEM.get_key(key='license_is_valid'),
                                     version=Cache_Version.SYSTEM.get_version())
        if license_is_valid:
            other = {'authentication': application_access_token.authentication,
                     'authentication_value': application_access_token.authentication_value}

        return {'application_id': application_access_token.application_id,
                'access_token': application_access_token.access_token,
                "is_active": application_access_token.is_active,
                'access_num': application_access_token.access_num,
                'white_active': application_access_token.white_active,
                'white_list': application_access_token.white_list,
                'show_source': application_access_token.show_source,
                'show_exec': application_access_token.show_exec,
                'language': application_access_token.language,
                **other,
                }
