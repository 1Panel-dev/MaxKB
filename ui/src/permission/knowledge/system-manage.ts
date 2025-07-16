import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const systemManage = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.ADMIN],
        [PermissionConst.SHARED_KNOWLEDGE_READ],
        [EditionConst.IS_EE],
        'OR',
      ),
      'OR',
    ),
  create: () => false,
  sync: () => false,
  vector: () => false,
  generate: () => false,
  edit: () => false,
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
  doc_download: () => false,

  knowledge_chat_user_edit: () => false,

  problem_create: () => false,
  problem_relate: () => false,
  problem_delete: () => false,
  problem_edit: () => false,
  
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
}

export default systemManage
