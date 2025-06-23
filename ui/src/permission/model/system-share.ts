import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  addModel: () => false,
  modify: () => false,
  paramSetting: () => false,
  delete: () => false,

}
export default share
