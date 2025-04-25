from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ModuleCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('module name'))

    parent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='root',
                                      label=_('parent id'))


class ModuleEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('module name'))
    parent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='root',
                                      label=_('parent id'))
