/**
 * 系统「应用资源管理」按钮权限（系统 > 资源管理 > 应用）。
 * 全局判定，无 workspace / 资源 id；系统页不存在的按钮直接返回 false。
 */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasEdition } from '../../core'
import { Edition } from '@/permission/core/common'

const system = {
  // —— 系统页不提供的操作 ——
  create: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  batchCleanStrategy: () => false,
  folderCreate: () => false,
  folderRead: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  // —— 资源操作 ——
/**
 * 系统「智能体」编辑权限
 */
  edit: () => canSys(P.RESOURCE_APPLICATION_EDIT),
/**
 * 系统「智能体」删除权限
 */
  delete: () => canSys(P.RESOURCE_APPLICATION_DELETE),
/**
 * 系统「智能体」复制权限
 */
  copy: () => canSys(P.RESOURCE_APPLICATION_COPY),
/**
 * 系统「智能体」导入权限
 */
  export: () => canSys(P.RESOURCE_APPLICATION_EXPORT),
/**
 * 系统「智能体」发布权限
 */
  publish: () => canSys(P.RESOURCE_APPLICATION_PUBLISH),
/**
 * 系统「智能体」发布到门户权限
 */
  portalUp: () => canSys(P.RESOURCE_APPLICATION_PORTAL_UP),
/**
 * 系统「智能体」从门户下架权限
 */
  portalDown: () => canSys(P.RESOURCE_APPLICATION_PORTAL_DOWN),
/**
 * 系统「智能体」资源授权权限
 */
  auth: () => canSys(P.RESOURCE_APPLICATION_AUTH),
/**
 * 系统「智能体」查看关联资源权限
 */
  relateMap: () => canSys(P.RESOURCE_APPLICATION_RELATE_RESOURCE_VIEW),
  debug: () => canSys(P.RESOURCE_APPLICATION_EDIT),

  // —— 触发器 ——
/**
 * 系统「智能体」「触发器」只读权限
 */
  triggerRead: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_READ),
/**
 * 系统「智能体」「触发器」创建权限
 */
  triggerCreate: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_CREATE),
/**
 * 系统「智能体」「触发器」编辑权限
 */
  triggerEdit: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_EDIT),
/**
 * 系统「智能体」「触发器」删除权限
 */
  triggerDelete: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_DELETE),

  // —— 概览 ——
/**
 * 系统「智能体」「概览」只读权限
 */
  overviewRead: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_READ),
/**
 * 系统「智能体」「概览」嵌入第三方权限
 */
  overviewEmbed: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_EMBED),
/**
 * 系统「智能体」「概览」访问限制权限
 */
  overviewAccess: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_ACCESS),
/**
 * 系统「智能体」「概览」显示设置权限
 */
  overviewDisplay: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_DISPLAY),
/**
 * 系统「智能体」「概览」API KEY权限
 */
  overviewApiKey: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_API_KEY),

  // —— 访问 / 访客 / 对话日志 ——
/**
 * 系统「智能体」「智能体接入」只读权限
 */
  accessRead: () => canSys(P.RESOURCE_APPLICATION_ACCESS_READ),
/**
 * 系统「智能体」「智能体接入」编辑权限
 */
  accessEdit: () => canSys(P.RESOURCE_APPLICATION_ACCESS_EDIT),
/**
 * 系统「智能体」「对话用户」只读权限
 */
  chatUserRead: () => canSys(P.RESOURCE_APPLICATION_CHAT_USER_READ),
/**
 * 系统「智能体」「对话用户」编辑权限
 */
  chatUserEdit: () => canSys(P.RESOURCE_APPLICATION_CHAT_USER_EDIT),
/**
 * 系统「智能体」「对话日志」只读权限
 */
  chatLogRead: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_READ),
/**
 * 系统「智能体」「对话日志」编辑权限
 */
  chatLogClear: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_CLEAR_POLICY),
/**
 * 系统「智能体」「对话日志」导出权限
 */
  chatLogExport: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_EXPORT),
/**
 * 系统「智能体」「对话日志」添加到知识库权限
 */
  chatLogAddKnowledge: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE),

  // —— 组合：跳转/进入应用 ——
  /**
   * 系统「智能体」只读权限
   * */
  read: () => canSys(P.RESOURCE_APPLICATION_READ) && hasEdition(Edition.EE),
}

export default system
