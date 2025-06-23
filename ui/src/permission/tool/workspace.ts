import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.ADMIN],
        [PermissionConst.SHARED_TOOL_READ],
        [EditionConst.IS_EE],
        'OR',
      ),
      'OR',
    ),
  delete: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_DELETE.getWorkspacePermission,
        PermissionConst.TOOL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR',
    ),
  create: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_CREATE.getWorkspacePermission,
        PermissionConst.TOOL_CREATE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  switch: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getWorkspacePermission,
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  edit: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getWorkspacePermission,
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  copy: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_EXPORT.getWorkspacePermission,
        PermissionConst.TOOL_EXPORT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  export: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_EXPORT.getWorkspacePermission,
        PermissionConst.TOOL_EXPORT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ), 
  debug: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_DEBUG.getWorkspacePermission,
        PermissionConst.TOOL_DEBUG.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ), 
     
}

export default workspace
