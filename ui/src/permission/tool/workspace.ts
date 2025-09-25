import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.ADMIN,RoleConst.USER.getWorkspaceRole,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
        [PermissionConst.TOOL_READ.getWorkspacePermission,PermissionConst.TOOL_READ.getWorkspacePermissionWorkspaceManageRole],
        [EditionConst.IS_EE],'OR'),
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
  import: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_IMPORT.getWorkspacePermission,
        PermissionConst.TOOL_IMPORT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),  
  folderCreate: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.TOOL_CREATE.getWorkspacePermission,
        PermissionConst.TOOL_CREATE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  delete: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_DELETE.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR',
    ),
  folderDelete: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_DELETE.getWorkspacePermission,
        PermissionConst.TOOL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR',
    ),
  switch: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  edit: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  folderEdit: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getWorkspacePermission,
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR',
    ),
  copy: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EXPORT.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_EXPORT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  export: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EXPORT.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_EXPORT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ), 
  auth: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.TOOL.getToolWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_RESOURCE_AUTHORIZATION.getToolWorkspaceResourcePermission(source_id),
        PermissionConst.TOOL_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ), 
  debug: () =>
    hasPermission(
      [ 
        RoleConst.USER.getWorkspaceRole,  
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TOOL_EDIT.getWorkspacePermission,
        PermissionConst.TOOL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ), 
     
}

export default workspace
