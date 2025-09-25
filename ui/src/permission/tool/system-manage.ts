import {hasPermission} from '@/utils/permission/index'
import {ComplexPermission} from '@/utils/permission/type'
import {EditionConst, PermissionConst, RoleConst} from '@/utils/permission/data'

const systemManage = {
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
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_DELETE,
      ],
      'OR',
    ),
  create: () => false,
  import: () => false,
  switch: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_EDIT,
      ],
      'OR',
    ),
  edit: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_EDIT,
      ],
      'OR',
    ),
  copy: () => false,
  export: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_EXPORT,
      ],
      'OR',
    ),
  debug: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_EDIT,
      ],
      'OR',
    ),

  auth: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.RESOURCE_TOOL_AUTH,
      ],
      'OR',
    ),
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,

}

export default systemManage
