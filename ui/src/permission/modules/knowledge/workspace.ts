/** 工作空间「知识库」按钮权限。 */

import { can } from '../../policy'
import { hasPermission, buildBaseResourcePermission, RoleConstants, Compare } from '../../core'
import { AggregatePermission, type Permission, Role } from '../../core/common'
import { getWorkspaceId } from '@/utils/resource-context'
import { PermissionConstants as P } from '../../core'

/** 按目标空间与知识库检查权限，保留管理员、所有者及工作空间授权。 */
export function canWorkspaceKnowledge(permission: Permission, id: string, workspaceId = getWorkspaceId()): boolean {
  return hasPermission([
    buildBaseResourcePermission(permission, id, workspaceId),
    permission.newWorkspacePermission(workspaceId),
    AggregatePermission.builder()
      .addRole(new Role(RoleConstants.USER.name, workspaceId))
      .addPermission(P.KNOWLEDGE.newResourcePermission(workspaceId, id))
      .compare(Compare.AND)
      .build(),
  ])
}

const workspace = {
  // —— 工作空间级 ——
  isShare: () => can(P.KNOWLEDGE_READ),
  create: () => can(P.KNOWLEDGE_CREATE),
  batchDelete: () => can(P.KNOWLEDGE_BATCH_DELETE),
  batchMove: () => can(P.KNOWLEDGE_BATCH_MOVE),

  // —— 知识库资源级 ——
  edit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EDIT, id),
  delete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DELETE, id),
  sync: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SYNC, id),
  vector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_VECTOR, id),
  generate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_GENERATE, id),
  export: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXPORT, id),
  publish: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_PUBLISH, id),
  auth: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_RESOURCE_AUTHORIZATION, id),
  relateMap: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_RELATE_RESOURCE_VIEW, id),
  authToWorkspace: () => false,

  mcpConfig: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_MCP_CONFIG, id),
  exportSkills: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXPORT_SKILLS, id),
  scheduledSyncRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SCHEDULED_SYNC_READ, id),
  scheduledSyncEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SCHEDULED_SYNC_EDIT, id),
  documentStrategyRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_STRATEGY_READ, id),
  documentStrategyEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_STRATEGY_EDIT, id),
  externalServiceRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_READ, id),
  externalServiceEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_EDIT, id),
  settingRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SETTING_READ, id),
  settingEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SETTING_EDIT, id),
  image: {
    read: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_READ, id),
    create: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_CREATE, id),
    edit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_EDIT, id),
    delete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_DELETE, id),
    download: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_DOWNLOAD_SOURCE_FILE, id),
    generate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_GENERATE, id),
    vector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_VECTOR, id),
    migrate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_MIGRATE, id),
    tag: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_TAG, id),
    replace: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_REPLACE, id),
    token: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_TOKEN, id),
  },

  // —— 文件夹 ——
  folderRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_READ, id),
  folderCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_CREATE, id),
  folderEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_EDIT, id),
  folderDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_DELETE, id),
  folderAuth: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_AUTH, id),
  folderManage: () => true,

  // —— 文档 ——
  docRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, id),
  docCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_CREATE, id),
  docEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_EDIT, id),
  docDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_DELETE, id),
  docSync: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_SYNC, id),
  docExport: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_EXPORT, id),
  docDownload: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE, id),
  docVector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_VECTOR, id),
  docToken: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_TOKEN, id),
  docGenerate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_GENERATE, id),
  docMigrate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_MIGRATE, id),
  docTag: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_TAG, id),
  docReplace: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_REPLACE, id),

  // —— 问题 ——
  problemRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_READ, id),
  problemCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_CREATE, id),
  problemEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_EDIT, id),
  problemDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_DELETE, id),
  problemRelate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_RELATE, id),

  // —— 术语库 ——
  termbaseRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_READ, id),
  termbaseCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_CREATE, id),
  termbaseEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_EDIT, id),
  termbaseDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_DELETE, id),

  // —— 标签 ——
  tagRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_READ, id),
  tagCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_CREATE, id),
  tagEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_EDIT, id),
  tagDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_DELETE, id),

  // —— 工作流 ——
  debug: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_READ, id),
  workflowEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_EDIT, id),
  workflowExport: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_EXPORT, id),

  // —— 访客 ——
  knowledgeChatUserRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_READ, id),
  knowledgeChatUserEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_EDIT, id),
  chatUserEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_EDIT, id),

  // —— 命中测试 ——
  hitTest: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_HIT_TEST, id),

  // —— 组合：进入知识库 ——
  read: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_READ, id),
}

export default workspace
