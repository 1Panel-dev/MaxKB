import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
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
  create: () =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermission,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  single: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_READ.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_READ.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  sync: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ), 
  vector: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  generate: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_GENERATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_GENERATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  setting: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  export: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_EXPORT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_EXPORT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  delete: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DELETE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_create: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_vector: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_generate: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_migrate: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_MIGRATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_MIGRATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ), 
  doc_edit: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_sync: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),      
  doc_delete: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_DELETE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ), 
  doc_export: (source_id:string) =>
    hasPermission(
      [
        RoleConst.ADMIN,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_EXPORT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_EXPORT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),       
}

export default workspace
