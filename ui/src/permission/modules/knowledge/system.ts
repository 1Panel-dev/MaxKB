/** 系统「知识库资源管理」按钮权限（系统 > 资源管理 > 知识库）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

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
/**
 * 系统「知识库」编辑权限
 */
  edit: () => canSys(P.RESOURCE_KNOWLEDGE_EDIT),
/**
 * 系统「知识库」删除权限
 */
  delete: () => canSys(P.RESOURCE_KNOWLEDGE_DELETE),
/**
 * 系统「知识库」同步权限
 */
  sync: () => canSys(P.RESOURCE_KNOWLEDGE_SYNC),
/**
 * 系统「知识库」向量化权限
 */
  vector: () => canSys(P.RESOURCE_KNOWLEDGE_VECTOR),
/**
 * 系统「知识库」生成问题权限
 */
  generate: () => canSys(P.RESOURCE_KNOWLEDGE_GENERATE),
/**
 * 系统「知识库」导出权限
 */
  export: () => canSys(P.RESOURCE_KNOWLEDGE_EXPORT),
/**
 * 系统「知识库」发布权限
 */
  publish: () => canSys(P.RESOURCE_KNOWLEDGE_PUBLISH),
/**
 * 系统「知识库」资源授权权限
 */
  auth: () => canSys(P.RESOURCE_KNOWLEDGE_AUTH),
/**
 * 系统「知识库」查看关联资源权限
 */
  relateMap: () => canSys(P.RESOURCE_KNOWLEDGE_RELATE_RESOURCE_VIEW),
/**
 * 系统「知识库」召回测试权限
 */
  hitTest: () => canSys(P.RESOURCE_KNOWLEDGE_HIT_TEST),
/**
 * 系统「知识库」MCP配置详情权限
 */
  mcpConfig: () => canSys(P.RESOURCE_KNOWLEDGE_MCP_CONFIG),
/**
 * 系统「知识库」导出权限
 */
  exportSkills: () => canSys(P.RESOURCE_KNOWLEDGE_EXPORT_SKILLS),
/**
 * 系统「知识库」「定时同步」只读权限
 */
  scheduledSyncRead: () => canSys(P.RESOURCE_KNOWLEDGE_SCHEDULED_SYNC_READ),
/**
 * 系统「知识库」「定时同步」编辑权限
 */
  scheduledSyncEdit: () => canSys(P.RESOURCE_KNOWLEDGE_SCHEDULED_SYNC_EDIT),
/**
 * 系统「知识库」文档只读权限
 */
  documentStrategyRead: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_STRATEGY_READ),
/**
 * 系统「知识库」文档编辑权限
 */
  documentStrategyEdit: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_STRATEGY_EDIT),
/**
 * 系统「知识库」「外部检索」只读权限
 */
  externalServiceRead: () => canSys(P.RESOURCE_KNOWLEDGE_EXTERNAL_SERVICE_READ),
/**
 * 系统「知识库」「外部检索」编辑权限
 */
  externalServiceEdit: () => canSys(P.RESOURCE_KNOWLEDGE_EXTERNAL_SERVICE_EDIT),
/**
 * 系统「知识库」「设置」只读权限
 */
  settingRead: () => canSys(P.RESOURCE_KNOWLEDGE_SETTING_READ),
/**
 * 系统「知识库」「设置」编辑权限
 */
  settingEdit: () => canSys(P.RESOURCE_KNOWLEDGE_SETTING_EDIT),
  image: {
    /**
    * 系统「知识库」「图片」只读权限
    */
    read: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_READ),
    /**
    * 系统「知识库」「图片」创建权限
    */
    create: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_CREATE),
    /**
    * 系统「知识库」「图片」编辑权限
    */
    edit: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_EDIT),
    /**
    * 系统「知识库」「图片」删除权限
    */
    delete: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_DELETE),
    /**
    * 系统「知识库」「图片」下载原文档权限
    */
    download: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_DOWNLOAD_SOURCE_FILE),
    /**
    * 系统「知识库」「图片」生成问题权限
    */
    generate: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_GENERATE),
    /**
    * 系统「知识库」「图片」向量化权限
    */
    vector: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_VECTOR),
    /**
    * 系统「知识库」「图片」迁移权限
    */
    migrate: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_MIGRATE),
    /**
    * 系统「知识库」「图片」标签设置权限
    */
    tag: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_TAG),
    /**
    * 系统「知识库」「图片」替换原文档权限
    */
    replace: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_REPLACE),
    /**
    * 系统「知识库」「图片」分词索引权限
    */
    token: () => canSys(P.RESOURCE_KNOWLEDGE_IMAGE_TOKEN),
  },

  // —— 文档 ——
/**
* 系统「知识库」「文档」只读权限
*/
  docRead: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_READ),
/**
* 系统「知识库」「文档」创建权限
*/
  docCreate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_CREATE),
/**
* 系统「知识库」「文档」编辑权限
*/
  docEdit: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT),
/**
* 系统「知识库」「文档」删除权限
*/
  docDelete: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_DELETE),
/**
* 系统「知识库」「文档」同步权限
*/
  docSync: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_SYNC),
/**
* 系统「知识库」「文档」导出权限
*/
  docExport: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT),
/**
* 系统「知识库」「文档」下载原文档权限
*/
  docDownload: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE),
/**
* 系统「知识库」「文档」向量化权限
*/
  docVector: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_VECTOR),
/**
* 系统「知识库」「文档」分词索引权限
*/
  docToken: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_TOKEN),
/**
* 系统「知识库」「文档」生成问题权限
*/
  docGenerate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_GENERATE),
/**
* 系统「知识库」「文档」迁移权限
*/
  docMigrate: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_MIGRATE),
/**
* 系统「知识库」「文档」标签设置权限
*/
  docTag: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_TAG),
/**
* 系统「知识库」「文档」替换原文档权限
*/
  docReplace: () => canSys(P.RESOURCE_KNOWLEDGE_DOCUMENT_REPLACE),

  // —— 问题 ——
/**
* 系统「知识库」「问题」只读权限
*/
  problemRead: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_READ),
/**
* 系统「知识库」「问题」创建权限
*/
  problemCreate: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_CREATE),
/**
* 系统「知识库」「问题」编辑权限
*/
  problemEdit: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_EDIT),
/**
* 系统「知识库」「问题」删除权限
*/
  problemDelete: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_DELETE),
/**
* 系统「知识库」「问题」关联分段权限
*/
  problemRelate: () => canSys(P.RESOURCE_KNOWLEDGE_PROBLEM_RELATE),

  // —— 术语库 ——
/**
* 系统「知识库」「词库」只读权限
*/
  termbaseRead: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_READ),
/**
* 系统「知识库」「词库」创建权限
*/
  termbaseCreate: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_CREATE),
/**
* 系统「知识库」「词库」编辑权限
*/
  termbaseEdit: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_EDIT),
/**
* 系统「知识库」「词库」删除权限
*/
  termbaseDelete: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_DELETE),
/**
 * 系统「知识库」「词库」导出权限
 */
  termbaseExport: () => canSys(P.RESOURCE_KNOWLEDGE_TERMBASE_EXPORT),
  // —— 标签 ——
/**
* 系统「知识库」「标签管理」只读权限
*/
  tagRead: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_READ),
/**
* 系统「知识库」「标签管理」创建权限
*/
  tagCreate: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_CREATE),
/**
* 系统「知识库」「标签管理」编辑权限
*/
  tagEdit: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_EDIT),
/**
* 系统「知识库」「标签管理」删除权限
*/
  tagDelete: () => canSys(P.RESOURCE_KNOWLEDGE_TAG_DELETE),

  // —— 工作流 ——
/**
* 系统「知识库」「工作流」只读权限
*/
  debug: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_READ),
/**
* 系统「知识库」「工作流」编辑权限
*/
  workflowEdit: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_EDIT),
/**
* 系统「知识库」「工作流」导出权限
*/
  workflowExport: () => canSys(P.RESOURCE_KNOWLEDGE_WORKFLOW_EXPORT),

  // —— 访客 ——
/**
* 系统「知识库」「对话用户」只读权限
*/
  knowledgeChatUserRead: () => canSys(P.RESOURCE_KNOWLEDGE_CHAT_USER_READ),
/**
* 系统「知识库」「对话用户」编辑权限
*/
  knowledgeChatUserEdit: () => canSys(P.RESOURCE_KNOWLEDGE_CHAT_USER_EDIT),

  // —— 外部检索服务 ——
/**
 * 系统「知识库」「外部检索服务」只读权限
 */
  knowledgeExternalServiceRead: () => canSys(P.RESOURCE_KNOWLEDGE_EXTERNAL_SERVICE_READ),
/**
 * 系统「知识库」「外部检索服务」编辑权限
 */
  knowledgeExternalServiceEdit: () => canSys(P.RESOURCE_KNOWLEDGE_EXTERNAL_SERVICE_EDIT),
  // —— 组合：进入知识库 ——
/**
* 系统「知识库」只读权限
*/
  read: () => canSys(P.RESOURCE_KNOWLEDGE_READ) && hasEdition(Edition.EE),
}

export default system
