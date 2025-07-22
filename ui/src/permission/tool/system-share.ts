import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  create: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_CREATE,
      ],
      'OR',
    ),
    import: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_IMPORT,
      ],
      'OR',
    ),
    delete: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_DELETE,
      ],
      'OR',
    ),
    switch: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_EDIT,
      ],
      'OR',
    ),
    edit: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_EDIT,
      ],
      'OR',
    ),
    copy: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_CREATE,
      ],
      'OR',
    ),
    export: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_EXPORT,
      ],
      'OR',
    ),
    debug: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_TOOL_DEBUG,
      ],
      'OR',
    ),
    
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
}
export default share
