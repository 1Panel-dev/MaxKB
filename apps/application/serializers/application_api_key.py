import hashlib

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from application.models.application_api_key import ApplicationApiKey
from common.cache_data.application_api_key_cache import get_application_api_key, del_application_api_key
from common.exception.app_exception import AppApiException


class ApplicationKeySerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApiKey
        fields = "__all__"


class EditApplicationKeySerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False, label=_("Availability"))

    allow_cross_domain = serializers.BooleanField(required=False,
                                                  label=_("Is cross-domain allowed"))

    cross_domain_list = serializers.ListSerializer(required=False,
                                                   child=serializers.CharField(required=True,
                                                                               label=_("Cross-domain address")),
                                                   label=_("Cross-domain list"))


class ApplicationKeySerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_('application id'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def generate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).filter(id=application_id).first()
        secret_key = 'agent-' + hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()
        application_api_key = ApplicationApiKey(id=uuid.uuid7(),
                                                secret_key=secret_key,
                                                user_id=application.user_id,
                                                application_id=application_id)
        application_api_key.save()
        return ApplicationKeySerializerModel(application_api_key).data

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        return [ApplicationKeySerializerModel(application_api_key).data for application_api_key in
                QuerySet(ApplicationApiKey).filter(application_id=application_id)]

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
        application_id = serializers.UUIDField(required=True, label=_('application id'))
        api_key_id = serializers.UUIDField(required=True, label=_('ApiKeyId'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Application id does not exist'))

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            api_key_id = self.data.get("api_key_id")
            application_id = self.data.get('application_id')
            application_api_key = QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                                     application_id=application_id).first()
            del_application_api_key(application_api_key.secret_key)
            application_api_key.delete()

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                EditApplicationKeySerializer(data=instance).is_valid(raise_exception=True)
            api_key_id = self.data.get("api_key_id")
            application_id = self.data.get('application_id')
            application_api_key = QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                                     application_id=application_id).first()
            if application_api_key is None:
                raise AppApiException(500, _('APIKey does not exist'))
            if 'is_active' in instance and instance.get('is_active') is not None:
                application_api_key.is_active = instance.get('is_active')
            if 'allow_cross_domain' in instance and instance.get('allow_cross_domain') is not None:
                application_api_key.allow_cross_domain = instance.get('allow_cross_domain')
            if 'cross_domain_list' in instance and instance.get('cross_domain_list') is not None:
                application_api_key.cross_domain_list = instance.get('cross_domain_list')
            application_api_key.save()
            # 写入缓存
            get_application_api_key('Bearer ' + application_api_key.secret_key, False)
            return True
