import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.ADMIN],
        [PermissionConst.MODEL_READ],
        [EditionConst.IS_EE],
        'OR',
      ),
      'OR',
    ),
  addModel: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_CREATE.getWorkspacePermission,
        PermissionConst.MODEL_CREATE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  modify: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_EDIT.getWorkspacePermission,
        PermissionConst.MODEL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  paramSetting: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_EDIT.getWorkspacePermission,
        PermissionConst.MODEL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  delete: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_DELETE.getWorkspacePermission,
        PermissionConst.MODEL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
}

export default workspace
