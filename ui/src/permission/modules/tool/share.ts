/** 系统「共享工具」按钮权限（系统 > 共享 > 工具）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

const share = {
  // —— 共享页不提供 ——
  isShare: () => false,
  batchDelete: () => false,
  batchMove: () => false,
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

  /**
   * 系统「共享工具」（系统 > 共享 > 工具）只读权限
   */
  read: () => canSys(P.SHARED_TOOL_READ) && hasEdition(Edition.EE),

  // —— 工具资源 ——
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）创建权限
   */
  create: () => canSys(P.SHARED_TOOL_CREATE),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）复制权限
   */
  copy: () => canSys(P.SHARED_TOOL_CREATE),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）导入权限
   */
  import: () => canSys(P.SHARED_TOOL_IMPORT),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）编辑权限
   */
  edit: () => canSys(P.SHARED_TOOL_EDIT),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）修改工具状态权限
   */
  switch: () => canSys(P.SHARED_TOOL_EDIT),
  debug: () => canSys(P.SHARED_TOOL_EDIT),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）删除权限
   */
  delete: () => canSys(P.SHARED_TOOL_DELETE),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）发布权限
   */
  publish: () => canSys(P.SHARED_TOOL_PUBLISH),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）导出权限
   */
  export: () => canSys(P.SHARED_TOOL_EXPORT),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）查看关联资源权限
   */
  relateMap: () => canSys(P.SHARED_TOOL_RELATE_RESOURCE_VIEW),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）查看执行记录权限
   */
  record: () => canSys(P.SHARED_TOOL_EXECUTE_RECORD),
  /**
   * 系统「共享工具」（系统 > 共享 > 工具）授权工作空间权限
   */
  authToWorkspace: () => canSys(P.SHARED_TOOL_TO_WORKSPACE),
}

export default share
