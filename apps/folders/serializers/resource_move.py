"""Validation shared by workspace resource moves."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def validate_move_folder(folder_model, workspace_id, folder_id):
    folder_id = serializers.CharField(max_length=64).run_validation(folder_id)
    if not folder_model.objects.filter(id=folder_id, workspace_id=workspace_id).exists():
        raise serializers.ValidationError({"folder_id": _("Folder does not exist in this workspace")})
    return folder_id


def validate_edit_folder(instance, resource):
    """Allow unchanged folder fields in full edit payloads, but require moves to use their own API."""
    if "folder_id" in instance and instance["folder_id"] != resource.folder_id:
        raise serializers.ValidationError({"folder_id": _("Use the move API to change the folder")})
