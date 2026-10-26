/** 工作空间「共享工具」按钮权限。 */

import { can } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 系统页不提供 ——
  isShare: () => false,
  create: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  import: () => false,
  debug: () => false,
  authToWorkspace: () => false,
  edit: () => false,
  switch: () => false,
  copy: () => false,
  delete: () => false,
  publish: () => false,
  export: () => false,
  auth: () => false,
  relateMap: () => false,
  record: () => false,
  triggerRead: () => false,
  triggerCreate: () => false,
  triggerEdit: () => false,
  triggerDelete: () => false,
  folderCreate: () => false,
  folderRead: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  // —— 工作空间级 ——
  /**
   * 工作空间「共享工具」只读权限
   */
  read: () => can(P.TOOL_READ),
}

export default workspace
