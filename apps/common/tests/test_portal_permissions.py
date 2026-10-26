# coding=utf-8

from django.test import SimpleTestCase

from common.auth.constants.category_constants import Category
from common.auth.constants.operate_constants import Operate
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants


class ApplicationPortalPermissionTests(SimpleTestCase):
    """智能体门户上下架权限已注册且分组/操作位与前端一致。"""

    def test_application_portal_up_permission(self):
        perm = PermissionConstants.APPLICATION_PORTAL_UP.value
        meta = PermissionConstants.APPLICATION_PORTAL_UP.meta
        self.assertEqual(perm.group.value, "APPLICATION")
        self.assertEqual(perm.operate, Operate.PORTAL_UP)
        self.assertEqual(perm.bit_index, 17)
        self.assertIn(RoleConstants.WORKSPACE_MANAGE, meta.role_list)
        self.assertIn(RoleConstants.USER, meta.role_list)
        self.assertEqual(meta.category, Category.WORKSPACE)

    def test_application_portal_down_permission(self):
        perm = PermissionConstants.APPLICATION_PORTAL_DOWN.value
        meta = PermissionConstants.APPLICATION_PORTAL_DOWN.meta
        self.assertEqual(perm.group.value, "APPLICATION")
        self.assertEqual(perm.operate, Operate.PORTAL_DOWN)
        self.assertEqual(perm.bit_index, 18)
        self.assertEqual(meta.category, Category.WORKSPACE)

    def test_resource_application_portal_up_permission(self):
        perm = PermissionConstants.RESOURCE_APPLICATION_PORTAL_UP.value
        meta = PermissionConstants.RESOURCE_APPLICATION_PORTAL_UP.meta
        self.assertEqual(perm.group.value, "SYSTEM_RESOURCE_APPLICATION")
        self.assertEqual(perm.operate, Operate.PORTAL_UP)
        self.assertEqual(perm.bit_index, 12)
        self.assertIn(RoleConstants.ADMIN, meta.role_list)
        self.assertEqual(meta.category, Category.RESOURCE)

    def test_resource_application_portal_down_permission(self):
        perm = PermissionConstants.RESOURCE_APPLICATION_PORTAL_DOWN.value
        meta = PermissionConstants.RESOURCE_APPLICATION_PORTAL_DOWN.meta
        self.assertEqual(perm.group.value, "SYSTEM_RESOURCE_APPLICATION")
        self.assertEqual(perm.operate, Operate.PORTAL_DOWN)
        self.assertEqual(perm.bit_index, 13)
        self.assertEqual(meta.category, Category.RESOURCE)

    def test_operate_values_match_frontend(self):
        self.assertEqual(Operate.PORTAL_UP.value, "READ+PORTAL_UP")
        self.assertEqual(Operate.PORTAL_DOWN.value, "READ+PORTAL_DOWN")
