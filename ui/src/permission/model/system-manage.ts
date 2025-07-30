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
  modify: (id: string) =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_EDIT], 'OR'),
  paramSetting: (id: string) =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_EDIT], 'OR'),
  delete: (id: string) =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_DELETE], 'OR'),

  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
}

export default systemManage
