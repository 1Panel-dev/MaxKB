import hashlib

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from application.models.application_api_key import ApplicationApiKey
from common.exception.app_exception import AppApiException


class ApplicationKeySerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApiKey
        fields = "__all__"


class Edit(serializers.Serializer):
    pass


class ApplicationKeySerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_('user id'))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    application_id = serializers.UUIDField(required=True, label=_('application id'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).filter(id=application_id).first()
        if application is None:
            raise AppApiException(1001, _("Application does not exist"))

    def generate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        application_id = self.data.get("application_id")
        application = QuerySet(Application).filter(id=application_id).first()
        secret_key = 'application-' + hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()
        application_api_key = ApplicationApiKey(id=uuid.uuid1(),
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
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        application_id = serializers.UUIDField(required=True, label=_('application id'))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
