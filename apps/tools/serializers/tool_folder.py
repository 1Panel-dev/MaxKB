# -*- coding: utf-8 -*-

from rest_framework import serializers

from tools.models import ToolFolder


class ToolFolderTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ToolFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id', 'children','create_time','update_time']

    def get_children(self, obj):
        return ToolFolderTreeSerializer(obj.get_children(), many=True).data


class ToolFolderFlatSerializer(serializers.ModelSerializer):
    """只序列化当前层的文件夹，不包含子节点"""

    class Meta:
        model = ToolFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id']
