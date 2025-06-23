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
  delete: () => false,
  create: () => false,
  switch: () => false,
  edit: () => false,
  copy: () => false,
  export: () => false,
  debug: () => false,

}

export default workspace
