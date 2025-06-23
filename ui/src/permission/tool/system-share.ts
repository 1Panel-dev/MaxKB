import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  delete: () => false,
  create: () => false,
  switch: () => false,
  edit: () => false,
  copy: () => false,
  export: () => false,
  debug: () => false,
}
export default share
