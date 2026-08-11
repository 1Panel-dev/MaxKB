from rest_framework import serializers
from role.models import Role, RolePermission, UserRole


class PermissionItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    enable = serializers.BooleanField()


class FeatureItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    permission = PermissionItemSerializer(many=True)
    enable = serializers.BooleanField()


class PermissionModuleSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    children = FeatureItemSerializer(many=True)


class RoleListResponse(serializers.Serializer):
    id = serializers.UUIDField()
    role_name = serializers.CharField()
    type = serializers.CharField()
    internal = serializers.BooleanField()
    user_count = serializers.IntegerField()


class RoleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "role_name", "type", "internal", "create_time"]


class CreateRoleSerializer(serializers.Serializer):
    role_name = serializers.CharField(max_length=64, required=True)
    role_type = serializers.CharField(required=False, allow_null=True)
    role_id = serializers.CharField(required=False, allow_null=True)


class SavePermissionSerializer(serializers.Serializer):
    id = serializers.CharField()
    enable = serializers.BooleanField()


class AddMemberSerializer(serializers.Serializer):
    members = serializers.ListField(child=serializers.DictField(), required=True)


class RoleMemberResponse(serializers.Serializer):
    user_relation_id = serializers.CharField()
    user_id = serializers.CharField()
    username = serializers.CharField()
    nick_name = serializers.CharField()
    workspace_name = serializers.SerializerMethodField()

    def get_workspace_name(self, obj):
        return obj.get("workspace_name", "-")
