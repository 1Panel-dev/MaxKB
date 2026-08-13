/** 系统「工具资源管理」按钮权限（系统 > 资源管理 > 工具）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const system = {
  // —— 系统页不提供 ——
  create: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  import: () => false,
  copy: () => false,
  jumpRead: () => false,
  authToWorkspace: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  read: () => canSys(P.RESOURCE_TOOL_READ),
  isShare: () => canSys(P.SHARED_TOOL_READ),

  // —— 工具资源 ——
  edit: () => canSys(P.RESOURCE_TOOL_EDIT),
  switch: () => canSys(P.RESOURCE_TOOL_EDIT),
  debug: () => canSys(P.RESOURCE_TOOL_EDIT),
  delete: () => canSys(P.RESOURCE_TOOL_DELETE),
  publish: () => canSys(P.RESOURCE_TOOL_PUBLISH),
  export: () => canSys(P.RESOURCE_TOOL_EXPORT),
  auth: () => canSys(P.RESOURCE_TOOL_AUTH),
  relateMap: () => canSys(P.RESOURCE_TOOL_RELATE_RESOURCE_VIEW),
  record: () => canSys(P.RESOURCE_TOOL_EXECUTE_RECORD),

  // —— 触发器 ——
  triggerRead: () => canSys(P.RESOURCE_TOOL_TRIGGER_READ),
  triggerCreate: () => canSys(P.RESOURCE_TOOL_TRIGGER_CREATE),
  triggerEdit: () => canSys(P.RESOURCE_TOOL_TRIGGER_EDIT),
  triggerDelete: () => canSys(P.RESOURCE_TOOL_TRIGGER_DELETE),
}

export default system
