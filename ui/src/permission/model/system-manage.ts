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
  addModel: () => false,
  modify: () => false,
  paramSetting: () => false,
  delete: () => false,
}

export default workspace
