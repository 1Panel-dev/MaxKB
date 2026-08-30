/**
 * 系统「应用资源管理」按钮权限（系统 > 资源管理 > 应用）。
 * 全局判定，无 workspace / 资源 id；系统页不存在的按钮直接返回 false。
 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

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
  edit: () => canSys(P.RESOURCE_APPLICATION_EDIT),
  delete: () => canSys(P.RESOURCE_APPLICATION_DELETE),
  copy: () => canSys(P.RESOURCE_APPLICATION_COPY),
  export: () => canSys(P.RESOURCE_APPLICATION_EXPORT),
  publish: () => canSys(P.RESOURCE_APPLICATION_PUBLISH),
  auth: () => canSys(P.RESOURCE_APPLICATION_AUTH),
  relateMap: () => canSys(P.RESOURCE_APPLICATION_RELATE_RESOURCE_VIEW),
  debug: () => canSys(P.RESOURCE_APPLICATION_EDIT),

  // —— 触发器 ——
  triggerRead: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_READ),
  triggerCreate: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_CREATE),
  triggerEdit: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_EDIT),
  triggerDelete: () => canSys(P.RESOURCE_APPLICATION_TRIGGER_DELETE),

  // —— 概览 ——
  overviewRead: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_READ),
  overviewEmbed: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_EMBED),
  overviewAccess: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_ACCESS),
  overviewDisplay: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_DISPLAY),
  overviewApiKey: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_API_KEY),

  // —— 访问 / 访客 / 对话日志 ——
  accessRead: () => canSys(P.RESOURCE_APPLICATION_ACCESS_READ),
  accessEdit: () => canSys(P.RESOURCE_APPLICATION_ACCESS_EDIT),
  chatUserRead: () => canSys(P.RESOURCE_APPLICATION_CHAT_USER_READ),
  chatUserEdit: () => canSys(P.RESOURCE_APPLICATION_CHAT_USER_EDIT),
  chatLogRead: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_READ),
  chatLogClear: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_CLEAR_POLICY),
  chatLogExport: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_EXPORT),
  chatLogAddKnowledge: () => canSys(P.RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE),

  // —— 组合：跳转/进入应用 ——
  jumpRead: () => canSys(P.RESOURCE_APPLICATION_OVERVIEW_READ) || canSys(P.RESOURCE_APPLICATION_READ),
}

export default system
