# -*- coding: utf-8 -*-

from rest_framework import serializers

from tools.models import ToolFolder


class ToolFolderTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ToolFolder
        fields = ['id', 'name', 'user_id', 'workspace_id', 'parent_id', 'children']

    def get_children(self, obj):
        return ToolFolderTreeSerializer(obj.get_children(), many=True).data
