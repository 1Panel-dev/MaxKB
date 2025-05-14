from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class FolderCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, label=_('folder name'))
    desc = serializers.CharField(
        required=False, max_length=200, allow_null=True, allow_blank=True, label=_('folder description')
    )

    parent_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default='root', label=_('parent id')
    )


class FolderEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('folder name'))
    desc = serializers.CharField(
        required=False, max_length=200, allow_null=True, allow_blank=True, label=_('folder description')
    )

    parent_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default='root', label=_('parent id')
    )
