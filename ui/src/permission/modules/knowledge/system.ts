/** 系统「知识库资源管理」按钮权限（系统 > 资源管理 > 知识库）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const system = {
  // —— 系统页不提供 ——
  create: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  chatUserEdit: () => false,
  authToWorkspace: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  isShare: () => canSys(P.SHARED_KNOWLEDGE_READ),

  // —— 知识库资源 ——
  edit: () => canSys(P.RESOURCE_KNOWLEDGE_EDIT),
  delete: () => canSys(P.RESOURCE_KNOWLEDGE_DELETE),
  sync: () => canSys(P.RESOURCE_KNOWLEDGE_SYNC),
  vector: () => canSys(P.RESOURCE_KNOWLEDGE_VECTOR),
  generate: () => canSys(P.RESOURCE_KNOWLEDGE_GENERATE),
  export: () => canSys(P.RESOURCE_KNOWLEDGE_EXPORT),
  publish: () => canSys(P.RESOURCE_KNOWLEDGE_PUBLISH),
  auth: () => canSys(P.RESOURCE_KNOWLEDGE_AUTH),
  relateMap: () => canSys(P.RESOURCE_KNOWLEDGE_RELATE_RESOURCE_VIEW),
  hitTest: () => canSys(P.RESOURCE_KNOWLEDGE_HIT_TEST),

  // —— 文档 ——
  docRead: () =>
    canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_READ) || canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_READ),
  docCreate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_CREATE),
  docEdit: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT),
  docDelete: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_DELETE),
  docSync: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_SYNC),
  docExport: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT),
  docDownload: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE),
  docVector: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_VECTOR),
  docToken: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_TOKEN),
  docGenerate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_GENERATE),
  docMigrate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_MIGRATE),
  docTag: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_TAG),
  docReplace: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_REPLACE),

  // —— 问题 ——
  problemRead: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_READ),
  problemCreate: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_CREATE),
  problemEdit: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_EDIT),
  problemDelete: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_DELETE),
  problemRelate: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_RELATE),

  // —— 术语库 ——
  termbaseRead: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_READ),
  termbaseCreate: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_CREATE),
  termbaseEdit: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_EDIT),
  termbaseDelete: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_DELETE),

  // —— 标签 ——
  tagRead: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_READ),
  tagCreate: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_CREATE),
  tagEdit: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_EDIT),
  tagDelete: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_DELETE),

  // —— 工作流 ——
  debug: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_READ),
  workflowEdit: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_EDIT),
  workflowExport: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_EXPORT),

  // —— 访客 ——
  knowledgeChatUserRead: () => canSys(P.RESOURCE_KNOWLEDGE_CHAT_USER_READ),
  knowledgeChatUserEdit: () => canSys(P.RESOURCE_KNOWLEDGE_CHAT_USER_EDIT),

  // —— 组合：进入知识库 ——
  jumpRead: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_READ),
}

export default system
