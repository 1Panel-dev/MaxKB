import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const share = {
  is_share: () => false,
  create: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_CREATE
      ],
      'OR'
    ),
  sync: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_SYNC
      ],
      'OR'
    ),
  vector: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_VECTOR
      ],
      'OR'
    ),
  generate: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_GENERATE
      ],
      'OR'
    ),
  edit: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_EDIT
      ],
      'OR'
    ),
  export: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_EXPORT
      ],
      'OR'
    ),
  delete: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DELETE
      ],
      'OR'
    ),
  
  doc_read: () => false,  
  doc_create: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
      ],
      'OR'
    ),
  doc_vector: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_VECTOR
      ],
      'OR'
    ),
  doc_generate: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_GENERATE
      ],
      'OR'
    ),
  doc_migrate: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_MIGRATE
      ],
      'OR'
    ),
  doc_edit: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_EDIT
      ],
      'OR'
    ),
  doc_sync: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_SYNC
      ],
      'OR'
    ),
  doc_delete: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_DELETE
      ],
      'OR'
    ),
  doc_export: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_EXPORT
      ],
      'OR'
    ),
  doc_download: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE
      ],
      'OR'
    ),
  doc_tag: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_TAG
      ],
      'OR'
    ),
  doc_replace: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_REPLACE
      ],
      'OR'
    ),
  problem_create: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_PROBLEM_CREATE
      ],
      'OR'
    ),
  knowledge_chat_user_read: () => false,  
  knowledge_chat_user_edit: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_EDIT
      ],
      'OR'
    ),
  problem_read: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_PROBLEM_READ
      ],
      'OR'
    ), 
  problem_relate: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_PROBLEM_RELATE
      ],
      'OR'
    ),
  problem_delete: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_PROBLEM_DELETE
      ],
      'OR'
    ),
  problem_edit: () => 
    hasPermission (
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_PROBLEM_EDIT
      ],
      'OR'
    ),
  tag_read: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_TAG_READ
      ],
      'OR',
    ),
  tag_create: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_TAG_CREATE
      ],
      'OR',
    ),
  tag_edit: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_TAG_EDIT
      ],
      'OR',
    ),
  tag_delete: () => 
    hasPermission(
      [
        RoleConst.ADMIN,
        PermissionConst.SHARED_KNOWLEDGE_TAG_DELETE
      ],
      'OR',
    ),

  chat_user_edit: () =>false,

  auth: () => false,
  folderRead: () => false,
  folderManage: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderAuth: () => false,
  folderDelete: () => false,
  hit_test: () => false,
}
export default share
