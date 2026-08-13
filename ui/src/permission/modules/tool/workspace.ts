/** 工作空间「工具」按钮权限。 */

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级 ——
  read: () => can(P.TOOL_READ),
  isShare: () => can(P.TOOL_READ),
  create: () => can(P.TOOL_CREATE),
  batchDelete: () => can(P.TOOL_BATCH_DELETE),
  batchMove: () => can(P.TOOL_BATCH_MOVE),
  import: () => can(P.TOOL_IMPORT),
  jumpRead: () => false,
  debug: () => false,
  authToWorkspace: () => false,

  // —— 工具资源级 ——
  edit: (id: string) => canRes(P.TOOL_EDIT, id),
  switch: (id: string) => canRes(P.TOOL_EDIT, id),
  copy: (id: string) => canRes(P.TOOL_EDIT, id),
  delete: (id: string) => canRes(P.TOOL_DELETE, id),
  publish: (id: string) => canRes(P.TOOL_PUBLISH, id),
  export: (id: string) => canRes(P.TOOL_EXPORT, id),
  auth: (id: string) => canRes(P.TOOL_RESOURCE_AUTHORIZATION, id),
  relateMap: (id: string) => canRes(P.TOOL_RELATE_RESOURCE_VIEW, id),
  record: (id: string) => canRes(P.TOOL_EXECUTE_RECORD, id),

  // —— 触发器 ——
  triggerRead: (id: string) => canRes(P.TOOL_TRIGGER_READ, id),
  triggerCreate: (id: string) => canRes(P.TOOL_TRIGGER_CREATE, id),
  triggerEdit: (id: string) => canRes(P.TOOL_TRIGGER_EDIT, id),
  triggerDelete: (id: string) => canRes(P.TOOL_TRIGGER_DELETE, id),

  // —— 文件夹 ——
  folderCreate: (id: string) => canRes(P.TOOL_FOLDER_CREATE, id),
  folderRead: (id: string) => canRes(P.TOOL_FOLDER_READ, id),
  folderEdit: (id: string) => canRes(P.TOOL_FOLDER_EDIT, id),
  folderDelete: (id: string) => canRes(P.TOOL_FOLDER_DELETE, id),
  folderAuth: (id: string) => canRes(P.TOOL_FOLDER_AUTH, id),
  folderManage: () => true,
}

export default workspace
