/** 工作空间「应用」按钮权限（工作空间内的应用列表 / 详情页）。 */

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级（无资源 id）——
/**
 * 工作空间「智能体」创建权限
 */
  create: () => can(P.APPLICATION_CREATE),
/**
 * 工作空间「智能体」批量删除权限
 */
  batchDelete: () => can(P.APPLICATION_BATCH_DELETE),
/**
 * 工作空间「智能体」批量移动权限
 */
  batchMove: () => can(P.APPLICATION_BATCH_MOVE),
/**
 * 工作空间「智能体」批量清除策略权限
 */
  batchCleanStrategy: () => can(P.APPLICATION_CHAT_LOG_CLEAR_POLICY),

  // —— 资源级（按应用 id）——
/**
 * 工作空间「智能体」编辑权限
 */
  edit: (id: string) => canRes(P.APPLICATION_EDIT, id),
/**
 * 工作空间「智能体」删除权限
 */
  delete: (id: string) => canRes(P.APPLICATION_DELETE, id),
/**
 * 工作空间「智能体」复制权限
 */
  copy: (id: string) => canRes(P.APPLICATION_COPY, id),
/**
 * 工作空间「智能体」导出权限
 */
  export: (id: string) => canRes(P.APPLICATION_EXPORT, id),
/**
 * 工作空间「智能体」发布权限
 */
  publish: (id: string) => canRes(P.APPLICATION_PUBLISH, id),
/**
 * 工作空间「智能体」上架到门户权限
 */
  portalUp: (id: string) => canRes(P.APPLICATION_PORTAL_UP, id),
/**
 * 工作空间「智能体」从门户下架权限
 */
  portalDown: (id: string) => canRes(P.APPLICATION_PORTAL_DOWN, id),
/**
 * 工作空间「智能体」资源授权权限
 */
  auth: (id: string) => canRes(P.APPLICATION_RESOURCE_AUTHORIZATION, id),
/**
 * 工作空间「智能体」查看关联资源权限
 */
  relateMap: (id: string) => canRes(P.APPLICATION_RELATE_RESOURCE_VIEW, id),
  debug: (id: string) => canRes(P.APPLICATION_READ, id),

  // —— 文件夹 ——
/**
 * 工作空间「智能体」「文件夹」创建权限
 */
  folderCreate: (id: string) => canRes(P.APPLICATION_FOLDER_CREATE, id),
/**
 * 工作空间「智能体」「文件夹」只读权限
 */
  folderRead: (id: string) => canRes(P.APPLICATION_FOLDER_READ, id),
/**
 * 工作空间「智能体」「文件夹」编辑权限
 */
  folderEdit: (id: string) => canRes(P.APPLICATION_FOLDER_EDIT, id),
/**
 * 工作空间「智能体」「文件夹」删除权限
 */
  folderDelete: (id: string) => canRes(P.APPLICATION_FOLDER_DELETE, id),
/**
 * 工作空间「智能体」「文件夹」资源授权权限
 */
  folderAuth: (id: string) => canRes(P.APPLICATION_FOLDER_AUTH, id),
  folderManage: (id: string) => canRes(P.APPLICATION_FOLDER_EDIT, id),

  // —— 触发器 ——
/**
 * 工作空间「智能体」「触发器」只读权限
 */
  triggerRead: (id: string) => canRes(P.APPLICATION_TRIGGER_READ, id),
/**
 * 工作空间「智能体」「触发器」创建权限
 */
  triggerCreate: (id: string) => canRes(P.APPLICATION_TRIGGER_CREATE, id),
/**
 * 工作空间「智能体」「触发器」编辑权限
 */
  triggerEdit: (id: string) => canRes(P.APPLICATION_TRIGGER_EDIT, id),
/**
 * 工作空间「智能体」「触发器」删除权限
 */
  triggerDelete: (id: string) => canRes(P.APPLICATION_TRIGGER_DELETE, id),

  // —— 概览 ——
/**
 * 工作空间「智能体」「概览」只读权限
 */
  overviewRead: (id: string) => canRes(P.APPLICATION_OVERVIEW_READ, id),
/**
 * 工作空间「智能体」「概览」嵌入第三方权限
 */
  overviewEmbed: (id: string) => canRes(P.APPLICATION_OVERVIEW_EMBED, id),
/**
 * 工作空间「智能体」「概览」访问限制权限
 */
  overviewAccess: (id: string) => canRes(P.APPLICATION_OVERVIEW_ACCESS, id),
/**
 * 工作空间「智能体」「概览」显示设置权限
 */
  overviewDisplay: (id: string) => canRes(P.APPLICATION_OVERVIEW_DISPLAY, id),
/**
 * 工作空间「智能体」「概览」API KEY权限
 */
  overviewApiKey: (id: string) => canRes(P.APPLICATION_OVERVIEW_API_KEY, id),

  // —— 访问 / 访客 / 对话日志 ——
/**
 * 工作空间「智能体」「智能体接入」只读权限
 */
  accessRead: (id: string) => canRes(P.APPLICATION_ACCESS_READ, id),
/**
 * 工作空间「智能体」「智能体接入」编辑权限
 */
  accessEdit: (id: string) => canRes(P.APPLICATION_ACCESS_EDIT, id),
/**
 * 工作空间「智能体」「对话用户」只读权限
 */
 chatUserRead: (id: string) => canRes(P.APPLICATION_CHAT_USER_READ, id),
/**
 * 工作空间「智能体」「对话用户」编辑权限
 */
  chatUserEdit: (id: string) => canRes(P.APPLICATION_CHAT_USER_EDIT, id),
/**
 * 工作空间「智能体」「对话日志」只读权限
 */
 chatLogRead: (id: string) => canRes(P.APPLICATION_CHAT_LOG_READ, id),
/**
 * 工作空间「智能体」「对话日志」清除策略权限
 */
  chatLogClear: (id: string) => canRes(P.APPLICATION_CHAT_LOG_CLEAR_POLICY, id),
/**
 * 工作空间「智能体」「对话日志」导出权限
 */
  chatLogExport: (id: string) => canRes(P.APPLICATION_CHAT_LOG_EXPORT, id),
/**
 * 工作空间「智能体」「对话日志」添加到知识库权限
 */
  chatLogAddKnowledge: (id: string) => canRes(P.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE, id),

  // —— 组合：跳转/进入应用（概览读 或 应用读 皆可）——
/**
 * 工作空间「智能体」只读权限
 */
  read: (id: string) => canRes(P.APPLICATION_OVERVIEW_READ, id) || canRes(P.APPLICATION_READ, id),
}

export default workspace
