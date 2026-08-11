from django.db import migrations, models
import uuid_utils.compat as uuid


def seed_builtin_roles(apps, schema_editor):
    Role = apps.get_model("role", "Role")
    RolePermission = apps.get_model("role", "RolePermission")

    builtin_roles = [
        {
            "id": uuid.uuid4(),
            "role_name": "系统管理员",
            "type": "ADMIN",
            "internal": True,
        },
        {
            "id": uuid.uuid4(),
            "role_name": "工作空间管理员",
            "type": "WORKSPACE_MANAGE",
            "internal": True,
        },
        {
            "id": uuid.uuid4(),
            "role_name": "普通用户",
            "type": "USER",
            "internal": True,
        },
    ]

    for role_data in builtin_roles:
        role = Role.objects.create(**role_data)
        # Give all three built-in roles the same full permissions
        all_perms = [
            {"permission_id": "SYSTEM_USER:READ+SETTING", "name": "设置"},
            {"permission_id": "SYSTEM_USER:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_USER:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_USER:READ+TRIGGER_READ", "name": "触发器"},
            {"permission_id": "SYSTEM_USER:READ+TRANSFER", "name": "转移到"},
            {"permission_id": "SYSTEM_USER:READ+EXPORT", "name": "导出"},
            {"permission_id": "SYSTEM_USER:READ+DELETE", "name": "删除"},
            {"permission_id": "SYSTEM_ROLE:READ+SETTING", "name": "设置"},
            {"permission_id": "SYSTEM_ROLE:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_ROLE:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_ROLE:READ+TRIGGER_READ", "name": "触发器"},
            {"permission_id": "SYSTEM_ROLE:READ+TRANSFER", "name": "转移到"},
            {"permission_id": "SYSTEM_ROLE:READ+EXPORT", "name": "导出"},
            {"permission_id": "SYSTEM_ROLE:READ+DELETE", "name": "删除"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+SETTING", "name": "设置"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ", "name": "触发器"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER", "name": "转移到"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+EXPORT", "name": "导出"},
            {"permission_id": "SYSTEM_RESOURCE_APPLICATION:READ+DELETE", "name": "删除"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+VECTOR", "name": "向量化"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+GENERATE", "name": "生成问题"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+TRANSFER", "name": "转移到"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+SETTING", "name": "设置"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+EXPORT", "name": "导出"},
            {"permission_id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+DELETE", "name": "删除"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+EDIT", "name": "编辑"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+INIT_PARAM", "name": "启动参数"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+TRIGGER_READ", "name": "触发器"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+TRANSFER", "name": "转移到"},
            {"permission_id": "SYSTEM_RESOURCE_TOOL:READ+DELETE", "name": "删除"},
            {"permission_id": "SYSTEM_RESOURCE_MODEL:READ+EDIT", "name": "编辑"},
            {"permission_id": "SYSTEM_RESOURCE_MODEL:READ+MODEL_PARAM", "name": "模型参数设置"},
            {"permission_id": "SYSTEM_RESOURCE_MODEL:READ+AUTH", "name": "资源授权"},
            {"permission_id": "SYSTEM_RESOURCE_MODEL:READ+RELATE_VIEW", "name": "查看关联资源"},
            {"permission_id": "SYSTEM_RESOURCE_MODEL:READ+DELETE", "name": "删除"},
        ]
        for p in all_perms:
            RolePermission.objects.create(role=role, **p, enable=True)


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("users", "__first__"),
    ]
    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("role_name", models.CharField(max_length=64, verbose_name="角色名称")),
                (
                    "type",
                    models.CharField(
                        max_length=32,
                        verbose_name="角色类型",
                        choices=[("ADMIN", "系统管理员"), ("USER", "普通用户"), ("WORKSPACE_MANAGE", "工作空间管理员")],
                    ),
                ),
                ("internal", models.BooleanField(default=False, verbose_name="是否内置")),
                ("create_time", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
            ],
            options={"db_table": "role"},
        ),
        migrations.CreateModel(
            name="RolePermission",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("permission_id", models.CharField(max_length=128, verbose_name="权限ID")),
                ("name", models.CharField(max_length=128, verbose_name="权限名称")),
                ("enable", models.BooleanField(default=False, verbose_name="是否启用")),
                (
                    "role",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="permissions", to="role.Role"),
                ),
            ],
            options={"db_table": "role_permission", "unique_together": [("role", "permission_id")]},
        ),
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("create_time", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="user_roles", to="users.User"),
                ),
                (
                    "role",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="user_roles", to="role.Role"),
                ),
            ],
            options={"db_table": "user_role", "unique_together": [("user", "role")]},
        ),
        migrations.RunPython(seed_builtin_roles),
    ]
