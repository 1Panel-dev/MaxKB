# -*- coding: utf-8 -*-

from rest_framework import serializers

from tools.models import ToolModule


class ToolModuleTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ToolModule
        fields = ['id', 'name', 'user_id', 'workspace_id', 'parent_id', 'children']

    def get_children(self, obj):
        return ToolModuleTreeSerializer(obj.get_children(), many=True).data
