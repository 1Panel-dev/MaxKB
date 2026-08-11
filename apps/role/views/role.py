import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.result import result
from role.models import Role, RolePermission, UserRole
from role.serializers.role import (
    RoleListResponse,
    CreateRoleSerializer,
    SavePermissionSerializer,
    AddMemberSerializer,
    PermissionModuleSerializer,
    RoleMemberResponse,
)


TEMPLATES = {
    "ADMIN": [
        {
            "id": "SYSTEM_MANAGEMENT",
            "name": "系统管理",
            "children": [
                {
                    "id": "SYSTEM_USER",
                    "name": "用户管理",
                    "permission": [
                        {"id": "SYSTEM_USER:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_USER:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_USER:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_USER:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_USER:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
                {
                    "id": "SYSTEM_ROLE",
                    "name": "角色管理",
                    "permission": [
                        {"id": "SYSTEM_ROLE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
            ],
        },
        {
            "id": "RESOURCE_APPLICATION",
            "name": "资源管理-智能体",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_APPLICATION",
                    "name": "智能体",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_KNOWLEDGE",
            "name": "资源管理-知识库",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_KNOWLEDGE",
                    "name": "知识库",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+VECTOR", "name": "向量化", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+GENERATE", "name": "生成问题", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_TOOL",
            "name": "资源管理-工具",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_TOOL",
                    "name": "工具",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+INIT_PARAM", "name": "启动参数", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_MODEL",
            "name": "资源管理-模型",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_MODEL",
                    "name": "模型",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+MODEL_PARAM", "name": "模型参数设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
    ],
    "WORKSPACE_MANAGE": [
        {
            "id": "SYSTEM_MANAGEMENT",
            "name": "系统管理",
            "children": [
                {
                    "id": "SYSTEM_USER",
                    "name": "用户管理",
                    "permission": [
                        {"id": "SYSTEM_USER:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_USER:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_USER:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_USER:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_USER:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
                {
                    "id": "SYSTEM_ROLE",
                    "name": "角色管理",
                    "permission": [
                        {"id": "SYSTEM_ROLE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
            ],
        },
        {
            "id": "RESOURCE_APPLICATION",
            "name": "资源管理-智能体",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_APPLICATION",
                    "name": "智能体",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_KNOWLEDGE",
            "name": "资源管理-知识库",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_KNOWLEDGE",
                    "name": "知识库",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+VECTOR", "name": "向量化", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+GENERATE", "name": "生成问题", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_TOOL",
            "name": "资源管理-工具",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_TOOL",
                    "name": "工具",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+INIT_PARAM", "name": "启动参数", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_MODEL",
            "name": "资源管理-模型",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_MODEL",
                    "name": "模型",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+MODEL_PARAM", "name": "模型参数设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
    ],
    "USER": [
        {
            "id": "SYSTEM_MANAGEMENT",
            "name": "系统管理",
            "children": [
                {
                    "id": "SYSTEM_USER",
                    "name": "用户管理",
                    "permission": [
                        {"id": "SYSTEM_USER:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_USER:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_USER:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_USER:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_USER:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_USER:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
                {
                    "id": "SYSTEM_ROLE",
                    "name": "角色管理",
                    "permission": [
                        {"id": "SYSTEM_ROLE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_ROLE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                },
            ],
        },
        {
            "id": "RESOURCE_APPLICATION",
            "name": "资源管理-智能体",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_APPLICATION",
                    "name": "智能体",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_APPLICATION:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_KNOWLEDGE",
            "name": "资源管理-知识库",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_KNOWLEDGE",
                    "name": "知识库",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+VECTOR", "name": "向量化", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+GENERATE", "name": "生成问题", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+SETTING", "name": "设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+EXPORT", "name": "导出", "enable": True},
                        {"id": "SYSTEM_RESOURCE_KNOWLEDGE:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_TOOL",
            "name": "资源管理-工具",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_TOOL",
                    "name": "工具",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+INIT_PARAM", "name": "启动参数", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRIGGER_READ", "name": "触发器", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+TRANSFER", "name": "转移到", "enable": True},
                        {"id": "SYSTEM_RESOURCE_TOOL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
        {
            "id": "RESOURCE_MODEL",
            "name": "资源管理-模型",
            "children": [
                {
                    "id": "SYSTEM_RESOURCE_MODEL",
                    "name": "模型",
                    "permission": [
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+EDIT", "name": "编辑", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+MODEL_PARAM", "name": "模型参数设置", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+AUTH", "name": "资源授权", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+RELATE_VIEW", "name": "查看关联资源", "enable": True},
                        {"id": "SYSTEM_RESOURCE_MODEL:READ+DELETE", "name": "删除", "enable": True},
                    ],
                    "enable": True,
                }
            ],
        },
    ],
}


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


def get_default_permission_tree(role_type: str) -> list:
    return TEMPLATES.get(role_type, TEMPLATES["USER"])


def flatten_permissions(tree: list) -> list:
    result_list = []
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                result_list.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "enable": p.get("enable", False),
                    }
                )
    return result_list


def apply_permissions(tree: list, perm_map: dict) -> list:
    for module in tree:
        for feature in module.get("children", []):
            for p in feature.get("permission", []):
                db_perm = perm_map.get(p["id"])
                if db_perm is not None:
                    p["enable"] = db_perm.enable
            feature["enable"] = any(pp["enable"] for pp in feature.get("permission", []))
        module["enable"] = any(f["enable"] for f in module.get("children", []))
    return tree


class RoleView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=["GET"], description=_("Get role list"), tags=[_("Role Management")])
    @has_permissions(PermissionConstants.ROLE_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        roles = Role.objects.annotate(user_count=Count("user_roles")).order_by("-internal", "create_time")
        internal_role = [r for r in roles if r.internal]
        custom_role = [r for r in roles if not r.internal]
        data = {
            "internal_role": [
                {
                    "id": str(r.id),
                    "role_name": r.role_name,
                    "type": r.type,
                    "internal": r.internal,
                    "user_count": r.user_count,
                }
                for r in internal_role
            ],
            "custom_role": [
                {
                    "id": str(r.id),
                    "role_name": r.role_name,
                    "type": r.type,
                    "internal": r.internal,
                    "user_count": r.user_count,
                }
                for r in custom_role
            ],
        }
        return result.success(data)

    @extend_schema(
        methods=["POST"],
        description=_("Create or update role"),
        request=CreateRoleSerializer,
        tags=[_("Role Management")],
    )
    @has_permissions(PermissionConstants.ROLE_CREATE, RoleConstants.ADMIN)
    def post(self, request: Request):
        serializer = CreateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        role_id = data.get("role_id")
        with transaction.atomic():
            if role_id:
                role = Role.objects.filter(id=role_id).first()
                if not role:
                    return result.error("角色不存在")
                role.role_name = data["role_name"]
                role.save()
                return result.success(
                    {
                        "id": str(role.id),
                        "role_name": role.role_name,
                        "type": role.type,
                        "internal": role.internal,
                    }
                )
            else:
                role_type = data.get("role_type", "USER")
                role = Role.objects.create(
                    role_name=data["role_name"],
                    type=role_type,
                    internal=False,
                )
                perm_tree = get_default_permission_tree(role_type)
                flat = flatten_permissions(perm_tree)
                RolePermission.objects.bulk_create(
                    [RolePermission(permission_id=p["id"], role=role, name=p["name"], enable=p["enable"]) for p in flat]
                )
                return result.success(
                    {
                        "id": str(role.id),
                        "role_name": role.role_name,
                        "type": role.type,
                        "internal": role.internal,
                    }
                )


class RoleOperateView(APIView):
    authentication_classes = [TokenAuth]

    @has_permissions(PermissionConstants.ROLE_DELETE, RoleConstants.ADMIN)
    def delete(self, request: Request, role_id: str):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return result.error("角色不存在")
        if role.internal:
            return result.error("内置角色不能删除")
        with transaction.atomic():
            UserRole.objects.filter(role=role).delete()
            RolePermission.objects.filter(role=role).delete()
            role.delete()
        return result.success("ok")


class RolePermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=["GET"], description=_("Get role permission tree"), tags=[_("Role Management")])
    @has_permissions(PermissionConstants.ROLE_READ, RoleConstants.ADMIN)
    def get(self, request: Request, role_id: str):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return result.error("角色不存在")

        if role.internal:
            tree = get_default_permission_tree(role.type)
            return result.success(tree)

        perms = RolePermission.objects.filter(role=role)
        perm_map = {p.permission_id: p for p in perms}
        tree = get_default_permission_tree(role.type)
        tree = apply_permissions(tree, perm_map)
        return result.success(tree)

    @extend_schema(
        methods=["POST"],
        description=_("Save role permissions"),
        request=SavePermissionSerializer(many=True),
        tags=[_("Role Management")],
    )
    @has_permissions(PermissionConstants.ROLE_EDIT, RoleConstants.ADMIN)
    def post(self, request: Request, role_id: str):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return result.error("角色不存在")
        if role.internal:
            return result.error("内置角色权限不能修改")

        serializer = SavePermissionSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for item in serializer.validated_data:
                RolePermission.objects.update_or_create(
                    role=role, permission_id=item["id"], defaults={"enable": item["enable"]}
                )
        return result.success("ok")


class RoleMemberView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=["GET"], description=_("Get role member list"), tags=[_("Role Management")])
    @has_permissions(PermissionConstants.ROLE_READ, RoleConstants.ADMIN)
    def get(self, request: Request, role_id: str, current_page: int, page_size: int):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return result.error("角色不存在")

        qs = UserRole.objects.filter(role=role).select_related("user")
        nick_name = request.query_params.get("nick_name")
        username = request.query_params.get("username")
        if nick_name:
            qs = qs.filter(user__nick_name__icontains=nick_name)
        if username:
            qs = qs.filter(user__username__icontains=username)

        total = qs.count()
        start = (current_page - 1) * page_size
        page_qs = qs[start : start + page_size]

        records = []
        for ur in page_qs:
            records.append(
                {
                    "user_relation_id": str(ur.id),
                    "user_id": str(ur.user.id),
                    "username": ur.user.username,
                    "nick_name": ur.user.nick_name,
                    "workspace_name": "-",
                }
            )

        return result.success({"total": total, "records": records})


class RoleAddMemberView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"], description=_("Add members to role"), request=AddMemberSerializer, tags=[_("Role Management")]
    )
    @has_permissions(PermissionConstants.ROLE_ADD_MEMBER, RoleConstants.ADMIN)
    def post(self, request: Request, role_id: str):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return result.error("角色不存在")

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for member in serializer.validated_data["members"]:
                user_id = member.get("user_id")
                if user_id:
                    UserRole.objects.get_or_create(user_id=user_id, role=role)
        return result.success("ok")


class RoleRemoveMemberView(APIView):
    authentication_classes = [TokenAuth]

    @has_permissions(PermissionConstants.ROLE_REMOVE_MEMBER, RoleConstants.ADMIN)
    def delete(self, request: Request, role_id: str, user_relation_id: str):
        UserRole.objects.filter(id=user_relation_id, role_id=role_id).delete()
        return result.success("ok")


class RoleTemplateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=["GET"], description=_("Get role permission template by type"), tags=[_("Role Management")])
    @has_permissions(PermissionConstants.ROLE_READ, RoleConstants.ADMIN)
    def get(self, request: Request, role_type: str):
        tree = get_default_permission_tree(role_type)
        return result.success(tree)


class UserPermissionsView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=["GET"], description=_("Get current user permissions"), tags=[_("Role Management")])
    def get(self, request: Request):
        from role.models import UserRole

        user = request.user
        role_ids = list(UserRole.objects.filter(user=user).values_list("role_id", flat=True))
        if not role_ids:
            legacy_type = user.role
            if legacy_type in ("ADMIN", "USER", "WORKSPACE_MANAGE"):
                role_ids = list(Role.objects.filter(type=legacy_type).values_list("id", flat=True))
        perms = RolePermission.objects.filter(role_id__in=role_ids, enable=True).values_list("permission_id", flat=True)
        return result.success(list(set(perms)))
