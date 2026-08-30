/** 系统「共享知识库」按钮权限（系统 > 共享 > 知识库）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const share = {
  // —— 共享页不提供 ——
  isShare: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  docRead: () => false,
  chatUserEdit: () => false,
  auth: () => false,
  knowledgeChatUserRead: () => false,
  hitTest: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  // —— 知识库资源 ——
  create: () => canSys(P.SHARED_KNOWLEDGE_CREATE),
  edit: () => canSys(P.SHARED_KNOWLEDGE_EDIT),
  delete: () => canSys(P.SHARED_KNOWLEDGE_DELETE),
  sync: () => canSys(P.SHARED_KNOWLEDGE_SYNC),
  vector: () => canSys(P.SHARED_KNOWLEDGE_VECTOR),
  generate: () => canSys(P.SHARED_KNOWLEDGE_GENERATE),
  export: () => canSys(P.SHARED_KNOWLEDGE_EXPORT),
  publish: () => canSys(P.SHARED_KNOWLEDGE_WORKFLOW_PUBLISH),
  relateMap: () => canSys(P.SHARED_KNOWLEDGE_RELATE_RESOURCE_VIEW),
  authToWorkspace: () => canSys(P.SHARED_KNOWLEDGE_TO_WORKSPACE),

  // —— 文档 ——
  docCreate: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_CREATE),
  docEdit: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_EDIT),
  docDelete: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_DELETE),
  docSync: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_SYNC),
  docExport: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_EXPORT),
  docDownload: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE),
  docVector: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_VECTOR),
  docToken: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_TOKEN),
  docGenerate: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_GENERATE),
  docMigrate: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_MIGRATE),
  docTag: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_TAG),
  docReplace: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_REPLACE),

  // —— 问题 ——
  problemRead: () => canSys(P.SHARED_KNOWLEDGE_PROBLEM_READ),
  problemCreate: () => canSys(P.SHARED_KNOWLEDGE_PROBLEM_CREATE),
  problemEdit: () => canSys(P.SHARED_KNOWLEDGE_PROBLEM_EDIT),
  problemDelete: () => canSys(P.SHARED_KNOWLEDGE_PROBLEM_DELETE),
  problemRelate: () => canSys(P.SHARED_KNOWLEDGE_PROBLEM_RELATE),

  // —— 术语库 ——
  termbaseRead: () => canSys(P.SHARED_KNOWLEDGE_TERMBASE_READ),
  termbaseCreate: () => canSys(P.SHARED_KNOWLEDGE_TERMBASE_CREATE),
  termbaseEdit: () => canSys(P.SHARED_KNOWLEDGE_TERMBASE_EDIT),
  termbaseDelete: () => canSys(P.SHARED_KNOWLEDGE_TERMBASE_DELETE),

  // —— 标签 ——
  tagRead: () => canSys(P.SHARED_KNOWLEDGE_TAG_READ),
  tagCreate: () => canSys(P.SHARED_KNOWLEDGE_TAG_CREATE),
  tagEdit: () => canSys(P.SHARED_KNOWLEDGE_TAG_EDIT),
  tagDelete: () => canSys(P.SHARED_KNOWLEDGE_TAG_DELETE),

  // —— 工作流 ——
  debug: () => canSys(P.SHARED_KNOWLEDGE_WORKFLOW_READ),
  workflowEdit: () => canSys(P.SHARED_KNOWLEDGE_WORKFLOW_EDIT),
  workflowExport: () => canSys(P.SHARED_KNOWLEDGE_WORKFLOW_EXPORT),

  // —— 访客 ——
  knowledgeChatUserEdit: () => canSys(P.SHARED_KNOWLEDGE_CHAT_USER_EDIT),

  // —— 组合：进入知识库 ——
  jumpRead: () => canSys(P.SHARED_KNOWLEDGE_DOCUMENT_READ) || canSys(P.SHARED_KNOWLEDGE_WORKFLOW_READ),
}

export default share
