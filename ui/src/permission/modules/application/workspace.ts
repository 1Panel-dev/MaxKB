/** 工作空间「应用」按钮权限（工作空间内的应用列表 / 详情页）。 */

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级（无资源 id）——
  create: () => can(P.APPLICATION_CREATE),
  batchDelete: () => can(P.APPLICATION_BATCH_DELETE),
  batchMove: () => can(P.APPLICATION_BATCH_MOVE),
  batchCleanStrategy: () => can(P.APPLICATION_CHAT_LOG_CLEAR_POLICY),

  // —— 资源级（按应用 id）——
  edit: (id: string) => canRes(P.APPLICATION_EDIT, id),
  delete: (id: string) => canRes(P.APPLICATION_DELETE, id),
  copy: (id: string) => canRes(P.APPLICATION_COPY, id),
  export: (id: string) => canRes(P.APPLICATION_EXPORT, id),
  publish: (id: string) => canRes(P.APPLICATION_PUBLISH, id),
  auth: (id: string) => canRes(P.APPLICATION_RESOURCE_AUTHORIZATION, id),
  relateMap: (id: string) => canRes(P.APPLICATION_RELATE_RESOURCE_VIEW, id),
  debug: (id: string) => canRes(P.APPLICATION_READ, id),

  // —— 文件夹 ——
  folderCreate: (id: string) => canRes(P.APPLICATION_FOLDER_CREATE, id),
  folderRead: (id: string) => canRes(P.APPLICATION_FOLDER_READ, id),
  folderEdit: (id: string) => canRes(P.APPLICATION_FOLDER_EDIT, id),
  folderDelete: (id: string) => canRes(P.APPLICATION_FOLDER_DELETE, id),
  folderAuth: (id: string) => canRes(P.APPLICATION_FOLDER_AUTH, id),
  folderManage: (id: string) => canRes(P.APPLICATION_FOLDER_EDIT, id),

  // —— 触发器 ——
  triggerRead: (id: string) => canRes(P.APPLICATION_TRIGGER_READ, id),
  triggerCreate: (id: string) => canRes(P.APPLICATION_TRIGGER_CREATE, id),
  triggerEdit: (id: string) => canRes(P.APPLICATION_TRIGGER_EDIT, id),
  triggerDelete: (id: string) => canRes(P.APPLICATION_TRIGGER_DELETE, id),

  // —— 概览 ——
  overviewRead: (id: string) => canRes(P.APPLICATION_OVERVIEW_READ, id),
  overviewEmbed: (id: string) => canRes(P.APPLICATION_OVERVIEW_EMBED, id),
  overviewAccess: (id: string) => canRes(P.APPLICATION_OVERVIEW_ACCESS, id),
  overviewDisplay: (id: string) => canRes(P.APPLICATION_OVERVIEW_DISPLAY, id),
  overviewApiKey: (id: string) => canRes(P.APPLICATION_OVERVIEW_API_KEY, id),

  // —— 访问 / 访客 / 对话日志 ——
  accessEdit: (id: string) => canRes(P.APPLICATION_ACCESS_EDIT, id),
  chatUserEdit: (id: string) => canRes(P.APPLICATION_CHAT_USER_EDIT, id),
  chatLogClear: (id: string) => canRes(P.APPLICATION_CHAT_LOG_CLEAR_POLICY, id),
  chatLogExport: (id: string) => canRes(P.APPLICATION_CHAT_LOG_EXPORT, id),
  chatLogAddKnowledge: (id: string) => canRes(P.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE, id),

  // —— 组合：跳转/进入应用（概览读 或 应用读 皆可）——
  jumpRead: (id: string) => canRes(P.APPLICATION_OVERVIEW_READ, id) || canRes(P.APPLICATION_READ, id),
}

export default workspace
