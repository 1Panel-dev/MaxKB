import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
const workspace = {
  is_share: () =>
    hasPermission(
      new ComplexPermission(
        [RoleConst.USER.getWorkspaceRole,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
        [PermissionConst.KNOWLEDGE_READ.getWorkspacePermission,PermissionConst.KNOWLEDGE_READ.getWorkspacePermissionWorkspaceManageRole],
        [EditionConst.IS_EE],'OR'),
      'OR',
    ),
  create: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermission,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  folderCreate: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermission,
        PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  sync: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_SYNC.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_SYNC.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  vector: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_VECTOR.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_VECTOR.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  generate: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_GENERATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_GENERATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  edit: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  folderEdit: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermission,
        PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  export: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_EXPORT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_EXPORT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  delete: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DELETE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  folderDelete: () =>
    hasPermission(
      [
        RoleConst.USER.getWorkspaceRole,
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DELETE.getWorkspacePermission,
        PermissionConst.KNOWLEDGE_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_read: () => false,  
  doc_create: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_vector: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_generate: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_migrate: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_MIGRATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_MIGRATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_edit: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_sync: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_SYNC.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_delete: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_DELETE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_export: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_EXPORT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_EXPORT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  doc_download: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ), 
  knowledge_chat_user_read: (source_id:string) => false,  
  knowledge_chat_user_edit: (source_id:string) => 
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_CHAT_USER_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_CHAT_USER_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ]
      ,'OR'
    ),
  problem_read: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_PROBLEM_READ.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_PROBLEM_READ.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),   
  problem_create: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_PROBLEM_CREATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_PROBLEM_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  problem_relate: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_PROBLEM_RELATE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_PROBLEM_RELATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  problem_delete: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_PROBLEM_DELETE.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_PROBLEM_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  problem_edit: (source_id:string) =>
    hasPermission(
      [
        new ComplexPermission([RoleConst.USER],[PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(source_id)],[],'AND'),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.KNOWLEDGE_PROBLEM_EDIT.getKnowledgeWorkspaceResourcePermission(source_id),
        PermissionConst.KNOWLEDGE_PROBLEM_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  hit_test: () => false,  
}

export default workspace
