import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  addModel: () =>
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
}
export default share
