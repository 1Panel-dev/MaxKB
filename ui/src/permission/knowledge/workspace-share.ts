import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspaceShare = {
  is_share: () => true,
  create: () => false,
  sync: () => false,
  vector: () => false,
  generate: () => false,
  edit: () => false,
  export: () => false,
  delete: () => false,
  auth: () => false,

  doc_read: () => false,  
  doc_create: () => false,
  doc_vector: () => false,
  doc_generate: () => false,
  doc_migrate: () => false,
  doc_edit: () => false,
  doc_sync: () => false,
  doc_delete: () => false,
  doc_export: () => false,
  doc_download: () => false,
  doc_tag: () => false,
  doc_replace: () => false,

  knowledge_chat_user_read: () => false,
  knowledge_chat_user_edit: () => false,

  tag_read: () => false,
  tag_create: () => false,
  tag_delete: () => false,
  tag_edit: () => false,
  
  problem_read: () => false,
  problem_create: () => false,
  problem_relate: () => false,
  problem_delete: () => false,
  problem_edit: () => false,
  chat_user_edit: () =>false,

  folderRead: () => false,
  folderManage: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderAuth: () => false,
  folderDelete: () => false,
  hit_test: () => false,
}

export default workspaceShare
