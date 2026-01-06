import {hasPermission} from '@/utils/permission/index'
import {ComplexPermission} from '@/utils/permission/type'
import {EditionConst, PermissionConst, RoleConst} from '@/utils/permission/data'

const share = {
  is_share: () => false,
  jump_read: () => false,
  create: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_MODEL_CREATE,
      ],
      'OR',
    ),
  modify: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_MODEL_EDIT,
      ],
      'OR',
    ),
  paramSetting: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_MODEL_EDIT,
      ],
      'OR',
    ),
  delete: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_MODEL_DELETE,
      ],
      'OR',
    ),
  auth: () => false,
  relate_map: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_MODEL_RELATE_RESOURCE_VIEW,
      ],
      'OR',
    ),
  folderRead: () => false,
  folderManage: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderAuth: () => false,
  folderDelete: () => false,
  debug: () => false,
}
export default share
