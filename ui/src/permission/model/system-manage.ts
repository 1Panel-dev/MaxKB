import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const systemManage = {
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
  create: () => false,
  modify: () => false,
  paramSetting: () => false,
  delete: () => false,

  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
}

export default systemManage
