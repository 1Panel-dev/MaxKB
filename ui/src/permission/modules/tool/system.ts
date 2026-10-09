/** 系统「工具资源管理」按钮权限（系统 > 资源管理 > 工具）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

const system = {
  // —— 系统页不提供 ——
  create: () => false,
  batchDelete: () => false,
  batchMove: () => false,
  import: () => false,
  copy: () => false,
  authToWorkspace: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）只读权限
   * */
  read: () => canSys(P.RESOURCE_TOOL_READ) && hasEdition(Edition.EE),
  isShare: () => canSys(P.SHARED_TOOL_READ),

  // —— 工具资源 ——
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）编辑权限
   * */
  edit: () => canSys(P.RESOURCE_TOOL_EDIT),
  switch: () => canSys(P.RESOURCE_TOOL_EDIT),
  debug: () => canSys(P.RESOURCE_TOOL_EDIT),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）删除权限
   * */
  delete: () => canSys(P.RESOURCE_TOOL_DELETE),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）发布权限
   * */
  publish: () => canSys(P.RESOURCE_TOOL_PUBLISH),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）导出权限
   * */
  export: () => canSys(P.RESOURCE_TOOL_EXPORT),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）资源授权权限
   * */
  auth: () => canSys(P.RESOURCE_TOOL_AUTH),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）查看关联资源权限
   * */
  relateMap: () => canSys(P.RESOURCE_TOOL_RELATE_RESOURCE_VIEW),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）查看执行记录权限
   * */
  record: () => canSys(P.RESOURCE_TOOL_EXECUTE_RECORD),

  // —— 触发器 ——
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）查看触发器权限
   * */
  triggerRead: () => canSys(P.RESOURCE_TOOL_TRIGGER_READ),
  /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）创建触发器权限
   * */
  triggerCreate: () => canSys(P.RESOURCE_TOOL_TRIGGER_CREATE),
   /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）编辑触发器权限
   * */
  triggerEdit: () => canSys(P.RESOURCE_TOOL_TRIGGER_EDIT),
   /**
   * 系统「工具资源管理」（系统 > 资源管理 > 工具）删除触发器权限
   * */
  triggerDelete: () => canSys(P.RESOURCE_TOOL_TRIGGER_DELETE),
}

export default system
