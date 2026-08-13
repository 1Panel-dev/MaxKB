/** 系统「共享工具」按钮权限（系统 > 共享 > 工具）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const share = {
  // —— 共享页不提供 ——
  isShare: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  jumpRead: () => false,
  auth: () => false,
  triggerRead: () => false,
  triggerCreate: () => false,
  triggerEdit: () => false,
  triggerDelete: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  read: () => canSys(P.SHARED_TOOL_READ),

  // —— 工具资源 ——
  create: () => canSys(P.SHARED_TOOL_CREATE),
  copy: () => canSys(P.SHARED_TOOL_CREATE),
  import: () => canSys(P.SHARED_TOOL_IMPORT),
  edit: () => canSys(P.SHARED_TOOL_EDIT),
  switch: () => canSys(P.SHARED_TOOL_EDIT),
  debug: () => canSys(P.SHARED_TOOL_EDIT),
  delete: () => canSys(P.SHARED_TOOL_DELETE),
  publish: () => canSys(P.SHARED_TOOL_PUBLISH),
  export: () => canSys(P.SHARED_TOOL_EXPORT),
  relateMap: () => canSys(P.SHARED_TOOL_RELATE_RESOURCE_VIEW),
  record: () => canSys(P.SHARED_TOOL_EXECUTE_RECORD),
  authToWorkspace: () => canSys(P.SHARED_TOOL_TO_WORKSPACE),
}

export default share
