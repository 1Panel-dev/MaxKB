from rest_framework import serializers

from knowledge.models import KnowledgeFolder


class KnowledgeFolderTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id', 'children', 'create_time','update_time']

    def get_children(self, obj):
        return KnowledgeFolderTreeSerializer(obj.get_children(), many=True).data


class KnowledgeFolderFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id']
