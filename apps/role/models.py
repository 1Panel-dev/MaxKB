import uuid_utils.compat as uuid
from django.db import models


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=64, verbose_name="角色名称")
    type = models.CharField(
        max_length=32,
        verbose_name="角色类型",
        choices=[("ADMIN", "系统管理员"), ("USER", "普通用户"), ("WORKSPACE_MANAGE", "工作空间管理员")],
    )
    internal = models.BooleanField(default=False, verbose_name="是否内置")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "role"


class RolePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    permission_id = models.CharField(max_length=128, verbose_name="权限ID")
    name = models.CharField(max_length=128, verbose_name="权限名称")
    enable = models.BooleanField(default=False, verbose_name="是否启用")

    class Meta:
        db_table = "role_permission"
        unique_together = [("role", "permission_id")]


class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "user_role"
        unique_together = [("user", "role")]
