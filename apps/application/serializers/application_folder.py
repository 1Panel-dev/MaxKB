from rest_framework import serializers

from application.models import ApplicationFolder


class ApplicationFolderTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id', 'children','create_time','update_time']

    def get_children(self, obj):
        return ApplicationFolderTreeSerializer(obj.get_children(), many=True).data


class ApplicationFolderFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFolder
        fields = ['id', 'name', 'desc', 'user_id', 'workspace_id', 'parent_id']
