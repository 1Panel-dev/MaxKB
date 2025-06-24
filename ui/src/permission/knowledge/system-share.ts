import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  create: () => false,
  single: () => false,
  sync: () => false,
  vector: () => false,
  generate: () => false,
  setting: () => false,
  export: () => false,
  delete: () => false,
  
  doc_create: () => false,
  doc_vector: () => false,
  doc_generate: () => false,
  doc_migrate: () => false,
  doc_edit: () => false,
  doc_sync: () => false,
  doc_delete: () => false,
  doc_export: () => false,

  
}
export default share
