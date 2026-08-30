/** 工作空间「知识库」按钮权限。 */

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级 ——
  isShare: () => can(P.KNOWLEDGE_READ),
  create: () => can(P.KNOWLEDGE_CREATE),
  batchDelete: () => can(P.KNOWLEDGE_BATCH_DELETE),
  batchMove: () => can(P.KNOWLEDGE_BATCH_MOVE),

  // —— 知识库资源级 ——
  edit: (id: string) => canRes(P.KNOWLEDGE_EDIT, id),
  delete: (id: string) => canRes(P.KNOWLEDGE_DELETE, id),
  sync: (id: string) => canRes(P.KNOWLEDGE_SYNC, id),
  vector: (id: string) => canRes(P.KNOWLEDGE_VECTOR, id),
  generate: (id: string) => canRes(P.KNOWLEDGE_GENERATE, id),
  export: (id: string) => canRes(P.KNOWLEDGE_EXPORT, id),
  publish: (id: string) => canRes(P.KNOWLEDGE_WORKFLOW_PUBLISH, id),
  auth: (id: string) => canRes(P.KNOWLEDGE_RESOURCE_AUTHORIZATION, id),
  relateMap: (id: string) => canRes(P.KNOWLEDGE_RELATE_RESOURCE_VIEW, id),
  authToWorkspace: () => false,

  // —— 文件夹 ——
  folderRead: (id: string) => canRes(P.KNOWLEDGE_FOLDER_READ, id),
  folderCreate: (id: string) => canRes(P.KNOWLEDGE_FOLDER_CREATE, id),
  folderEdit: (id: string) => canRes(P.KNOWLEDGE_FOLDER_EDIT, id),
  folderDelete: (id: string) => canRes(P.KNOWLEDGE_FOLDER_DELETE, id),
  folderAuth: (id: string) => canRes(P.KNOWLEDGE_FOLDER_AUTH, id),
  folderManage: () => true,

  // —— 文档 ——
  docRead: () => false,
  docCreate: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_CREATE, id),
  docEdit: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_EDIT, id),
  docDelete: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_DELETE, id),
  docSync: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_SYNC, id),
  docExport: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_EXPORT, id),
  docDownload: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE, id),
  docVector: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_VECTOR, id),
  docToken: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_TOKEN, id),
  docGenerate: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_GENERATE, id),
  docMigrate: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_MIGRATE, id),
  docTag: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_TAG, id),
  docReplace: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_REPLACE, id),

  // —— 问题 ——
  problemRead: (id: string) => canRes(P.KNOWLEDGE_PROBLEM_READ, id),
  problemCreate: (id: string) => canRes(P.KNOWLEDGE_PROBLEM_CREATE, id),
  problemEdit: (id: string) => canRes(P.KNOWLEDGE_PROBLEM_EDIT, id),
  problemDelete: (id: string) => canRes(P.KNOWLEDGE_PROBLEM_DELETE, id),
  problemRelate: (id: string) => canRes(P.KNOWLEDGE_PROBLEM_RELATE, id),

  // —— 术语库 ——
  termbaseRead: (id: string) => canRes(P.KNOWLEDGE_TERMBASE_READ, id),
  termbaseCreate: (id: string) => canRes(P.KNOWLEDGE_TERMBASE_CREATE, id),
  termbaseEdit: (id: string) => canRes(P.KNOWLEDGE_TERMBASE_EDIT, id),
  termbaseDelete: (id: string) => canRes(P.KNOWLEDGE_TERMBASE_DELETE, id),

  // —— 标签 ——
  tagRead: (id: string) => canRes(P.KNOWLEDGE_TAG_READ, id),
  tagCreate: (id: string) => canRes(P.KNOWLEDGE_TAG_CREATE, id),
  tagEdit: (id: string) => canRes(P.KNOWLEDGE_TAG_EDIT, id),
  tagDelete: (id: string) => canRes(P.KNOWLEDGE_TAG_DELETE, id),

  // —— 工作流 ——
  debug: (id: string) => canRes(P.KNOWLEDGE_WORKFLOW_READ, id),
  workflowEdit: (id: string) => canRes(P.KNOWLEDGE_WORKFLOW_EDIT, id),
  workflowExport: (id: string) => canRes(P.KNOWLEDGE_WORKFLOW_EXPORT, id),

  // —— 访客 ——
  knowledgeChatUserRead: (_id: string) => false,
  knowledgeChatUserEdit: (id: string) => canRes(P.KNOWLEDGE_CHAT_USER_EDIT, id),
  chatUserEdit: (id: string) => canRes(P.KNOWLEDGE_CHAT_USER_EDIT, id),

  // —— 命中测试 ——
  hitTest: () => false,

  // —— 组合：进入知识库 ——
  jumpRead: (id: string) => canRes(P.KNOWLEDGE_DOCUMENT_READ, id) || canRes(P.KNOWLEDGE_WORKFLOW_READ, id),
}

export default workspace
