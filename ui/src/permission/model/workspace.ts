import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.USER.getWorkspaceRole,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
        [PermissionConst.MODEL_READ.getWorkspacePermission,PermissionConst.MODEL_READ.getWorkspacePermissionWorkspaceManageRole],
        [EditionConst.IS_EE],'OR'),
      'OR',
    ),
  create: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_CREATE.getWorkspacePermission,
        PermissionConst.MODEL_CREATE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  folderRead: () => true,
  folderManage: () => true,
  folderAuth: () => false,
  folderCreate: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_CREATE.getWorkspacePermission,
        PermissionConst.MODEL_CREATE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  modify: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.MODEL.getModelWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.MODEL_EDIT.getModelWorkspaceResourcePermission(source_id),
        PermissionConst.MODEL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  auth: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.MODEL.getModelWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.MODEL_RESOURCE_AUTHORIZATION.getModelWorkspaceResourcePermission(source_id),
        PermissionConst.MODEL_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  folderEdit: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_EDIT.getWorkspacePermission,
        PermissionConst.MODEL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  paramSetting: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.MODEL.getModelWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.MODEL_EDIT.getModelWorkspaceResourcePermission(source_id),
        PermissionConst.MODEL_EDIT.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  delete: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.MODEL.getModelWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.MODEL_DELETE.getModelWorkspaceResourcePermission(source_id),
        PermissionConst.MODEL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  folderDelete: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        RoleConst.USER.getWorkspaceRole,
        PermissionConst.MODEL_DELETE.getWorkspacePermission,
        PermissionConst.MODEL_DELETE.getWorkspacePermissionWorkspaceManageRole
      ],
      'OR'
    ),
  debug: () => false,
}

export default workspace
