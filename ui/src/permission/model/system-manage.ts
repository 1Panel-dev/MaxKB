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
  modify: () =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_EDIT], 'OR'),
  paramSetting: () =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_EDIT], 'OR'),
  delete: () =>
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_DELETE], 'OR'),

  auth: () => 
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_MODEL_AUTH], 'OR'),
  
  folderRead: () => false,
  folderManage: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderAuth: () => false,
  folderDelete: () => false,
  debug: () => false,
  
}

export default systemManage
