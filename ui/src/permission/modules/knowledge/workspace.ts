/** 工作空间「知识库」按钮权限。 */

import { can, canRes } from '../../policy'
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
/**
 * 工作空间「知识库」只读权限
 */
  isShare: () => can(P.KNOWLEDGE_READ),
/**
 * 工作空间「知识库」创建权限
 */
  create: () => can(P.KNOWLEDGE_CREATE),
/**
 * 工作空间「知识库」批量删除权限
 */
  batchDelete: () => can(P.KNOWLEDGE_BATCH_DELETE),
/**
 * 工作空间「知识库」批量移动权限
 */
  batchMove: () => can(P.KNOWLEDGE_BATCH_MOVE),

  // —— 知识库资源级 ——
/**
 * 工作空间「知识库」编辑权限
 */
  edit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EDIT, id),
  /** 工作空间「知识库」移动权限。 */
  move: (id: string) => canRes(P.KNOWLEDGE_MOVE, id),
/**
 * 工作空间「知识库」删除权限
 */
  delete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DELETE, id),
/**
 * 工作空间「知识库」同步权限
 */
  sync: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SYNC, id),
/**
 * 工作空间「知识库」向量化权限
 */
  vector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_VECTOR, id),
/**
 * 工作空间「知识库」生成问题权限
 */
  generate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_GENERATE, id),
/**
 * 工作空间「知识库」导出权限
 */
  export: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXPORT, id),
/**
 * 工作空间「知识库」发布权限
 */
  publish: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_PUBLISH, id),
/**
 * 工作空间「知识库」资源授权权限
 */
  auth: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_RESOURCE_AUTHORIZATION, id),
/**
 * 工作空间「知识库」查看关联资源权限
 */
  relateMap: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_RELATE_RESOURCE_VIEW, id),
  authToWorkspace: () => false,
/**
 * 工作空间「知识库」MCP配置详情权限
 */
  mcpConfig: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_MCP_CONFIG, id),
/**
 * 工作空间「知识库」导出权限
 */
  exportSkills: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXPORT_SKILLS, id),
/**
 * 工作空间「知识库」「定时同步」只读权限
 */
  scheduledSyncRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SCHEDULED_SYNC_READ, id),
/**
 * 工作空间「知识库」「定时同步」编辑权限
 */
  scheduledSyncEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SCHEDULED_SYNC_EDIT, id),
/**
 * 工作空间「知识库」文档只读权限
 */
  documentStrategyRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_STRATEGY_READ, id),
/**
 * 工作空间「知识库」文档编辑权限
 */
  documentStrategyEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_STRATEGY_EDIT, id),
/**
 * 工作空间「知识库」「外部检索」只读权限
 */
  externalServiceRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_READ, id),
/**
 * 工作空间「知识库」「外部检索」编辑权限
 */
  externalServiceEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_EDIT, id),
/**
 * 工作空间「知识库」「设置」只读权限
 */
  settingRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SETTING_READ, id),
/**
 * 工作空间「知识库」「设置」编辑权限
 */
  settingEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_SETTING_EDIT, id),
  image: {
    /**
    * 工作空间「知识库」「图片」只读权限
    */
    read: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_READ, id),
    /**
    * 工作空间「知识库」「图片」创建权限
    */
    create: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_CREATE, id),
    /**
    * 工作空间「知识库」「图片」编辑权限
    */
    edit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_EDIT, id),
    /**
    * 工作空间「知识库」「图片」删除权限
    */
    delete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_DELETE, id),
    /**
    * 工作空间「知识库」「图片」下载原文档权限
    */
    download: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_DOWNLOAD_SOURCE_FILE, id),
    /**
    * 工作空间「知识库」「图片」生成问题权限
    */
    generate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_GENERATE, id),
    /**
    * 工作空间「知识库」「图片」向量化权限
    */
    vector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_VECTOR, id),
    /**
    * 工作空间「知识库」「图片」迁移权限
    */
    migrate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_MIGRATE, id),
    /**
    * 工作空间「知识库」「图片」标签设置权限
    */
    tag: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_TAG, id),
    /**
    * 工作空间「知识库」「图片」替换原文件权限
    */
    replace: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_REPLACE, id),
    /**
    * 工作空间「知识库」「图片」分词索引权限
    */
    token: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_TOKEN, id),
  },

  // —— 文件夹 ——
/**
 * 工作空间「知识库」「文件夹」只读权限
 */
  folderRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_READ, id),
/**
 * 工作空间「知识库」「文件夹」创建权限
 */
  folderCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_CREATE, id),
/**
 * 工作空间「知识库」「文件夹」编辑权限
 */
  folderEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_EDIT, id),
/**
 * 工作空间「知识库」「文件夹」删除权限
 */
  folderDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_DELETE, id),
/**
 * 工作空间「知识库」「文件夹」资源授权权限
 */
  folderAuth: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_FOLDER_AUTH, id),
  folderManage: () => true,

  // —— 文档 ——
/**
 * 工作空间「知识库」「文档」只读权限
 */
  docRead: (id: string) =>canRes(P.KNOWLEDGE_DOCUMENT_READ, id),
/**
 * 工作空间「知识库」「文档」创建权限
 */
  docCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_CREATE, id),
/**
 * 工作空间「知识库」「文档」编辑权限
 */
  docEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_EDIT, id),
/**
 * 工作空间「知识库」「文档」删除权限
 */
  docDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_DELETE, id),
/**
 * 工作空间「知识库」「文档」同步权限
 */
  docSync: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_SYNC, id),
/**
 * 工作空间「知识库」「文档」导出权限
 */
  docExport: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_EXPORT, id),
/**
 * 工作空间「知识库」「文档」下载原文档权限
 */
  docDownload: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE, id),
/**
 * 工作空间「知识库」「文档」向量化权限
 */
  docVector: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_VECTOR, id),
/**
 * 工作空间「知识库」「文档」分词索引权限
 */
  docToken: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_TOKEN, id),
/**
 * 工作空间「知识库」「文档」生成问题权限
 */
  docGenerate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_GENERATE, id),
/**
 * 工作空间「知识库」「文档」迁移权限
 */
  docMigrate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_MIGRATE, id),
/**
 * 工作空间「知识库」「文档」标签设置权限
 */
  docTag: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_TAG, id),
/**
 * 工作空间「知识库」「文档」替换原文档权限
 */
  docReplace: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_REPLACE, id),

  // —— 问题 ——
/**
 * 工作空间「知识库」「问题」只读权限
 */
  problemRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_READ, id),
/**
 * 工作空间「知识库」「问题」创建权限
 */
  problemCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_CREATE, id),
/**
 * 工作空间「知识库」「问题」编辑权限
 */
  problemEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_EDIT, id),
/**
 * 工作空间「知识库」「问题」删除权限
 */
  problemDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_DELETE, id),
/**
 * 工作空间「知识库」「问题」关联分段权限
 */
  problemRelate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_PROBLEM_RELATE, id),

  // —— 术语库 ——
/**
 * 工作空间「知识库」「词库」只读权限
 */
  termbaseRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_READ, id),
/**
 * 工作空间「知识库」「词库」创建权限
 */
  termbaseCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_CREATE, id),
/**
 * 工作空间「知识库」「词库」编辑权限
 */
  termbaseEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_EDIT, id),
/**
 * 工作空间「知识库」「词库」删除权限
 */
  termbaseDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_DELETE, id),
/**
 * 工作空间「知识库」「词库」导出权限
 */
  termbaseExport: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TERMBASE_EXPORT, id),
  // —— 标签 ——
/**
 * 工作空间「知识库」「标签管理」只读权限
 */
  tagRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_READ, id),
/**
 * 工作空间「知识库」「标签管理」创建权限
 */
  tagCreate: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_CREATE, id),
/**
 * 工作空间「知识库」「标签管理」编辑权限
 */
  tagEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_EDIT, id),
/**
 * 工作空间「知识库」「标签管理」删除权限
 */
  tagDelete: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_TAG_DELETE, id),

  // —— 工作流 ——
/**
 * 工作空间「知识库」「工作流」只读权限
 */
  debug: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_READ, id),
/**
 * 工作空间「知识库」「工作流」编辑权限
 */
  workflowEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_EDIT, id),
/**
 * 工作空间「知识库」「工作流」导出权限
 */
  workflowExport: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_WORKFLOW_EXPORT, id),

  // —— 访客 ——
/**
 * 工作空间「知识库」「对话用户」只读权限
 */
  knowledgeChatUserRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_READ, id),
/**
 * 工作空间「知识库」「对话用户」编辑权限
 */
  knowledgeChatUserEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_EDIT, id),
/**
 * 工作空间「知识库」「对话用户」编辑权限
 */
  chatUserEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_CHAT_USER_EDIT, id),

  // —— 命中测试 ——
/**
 * 工作空间「知识库」「命中测试」只读权限
 */
  hitTest: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_HIT_TEST, id),

  // —— 外部检索服务 ——
/**
 * 工作空间「知识库」「外部检索服务」只读权限
 */
  knowledgeExternalServiceRead: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_READ, id),
/**
 * 工作空间「知识库」「外部检索服务」 编辑权限
 */
  knowledgeExternalServiceEdit: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_EXTERNAL_SERVICE_EDIT, id),


  // —— 组合：进入知识库 ——
/**
 * 工作空间「知识库」只读权限
 */
  read: (id: string) => canWorkspaceKnowledge(P.KNOWLEDGE_READ, id),
}

export default workspace
