/** 工作空间「工具」按钮权限。 */

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级 ——
  /**
   * 工作空间「工具」只读权限
   */
  read: () => can(P.TOOL_READ),
  isShare: () => can(P.TOOL_READ),
  /**
   * 工作空间「工具」创建权限
   */
  create: () => can(P.TOOL_CREATE),
  /**
   * 工作空间「工具」批量删除权限
   */
  batchDelete: () => can(P.TOOL_BATCH_DELETE),
  /**
   * 工作空间「工具」批量移动权限
   */
  batchMove: () => can(P.TOOL_BATCH_MOVE),
  /**
   * 工作空间「工具」导入权限
   */
  import: () => can(P.TOOL_IMPORT),
  debug: () => false,
  authToWorkspace: () => false,

  // —— 工具资源级 ——
  /**
   * 工作空间「工具」编辑权限
   */
  edit: (id: string) => canRes(P.TOOL_EDIT, id),
  switch: (id: string) => canRes(P.TOOL_EDIT, id),
  /**
   * 工作空间「工具」复制权限
   */
  copy: (id: string) => canRes(P.TOOL_EDIT, id),
  /**
   * 工作空间「工具」删除权限
   */
  delete: (id: string) => canRes(P.TOOL_DELETE, id),
  /**
   * 工作空间「工具」发布权限
   */
  publish: (id: string) => canRes(P.TOOL_PUBLISH, id),
  /**
   * 工作空间「工具」导出权限
   */
  export: (id: string) => canRes(P.TOOL_EXPORT, id),
  /**
   * 工作空间「工具」资源授权权限
   */
  auth: (id: string) => canRes(P.TOOL_RESOURCE_AUTHORIZATION, id),
  /**
   * 工作空间「工具」查看关联资源权限
   */
  relateMap: (id: string) => canRes(P.TOOL_RELATE_RESOURCE_VIEW, id),
  /**
   * 工作空间「工具」查看执行记录权限
   */
  record: (id: string) => canRes(P.TOOL_EXECUTE_RECORD, id),

  // —— 触发器 ——
  /**
   * 工作空间「工具」查看触发器权限
   */
  triggerRead: (id: string) => canRes(P.TOOL_TRIGGER_READ, id),
  /**
   * 工作空间「工具」创建触发器权限
   */
  triggerCreate: (id: string) => canRes(P.TOOL_TRIGGER_CREATE, id),
  /**
   * 工作空间「工具」编辑触发器权限
   */
  triggerEdit: (id: string) => canRes(P.TOOL_TRIGGER_EDIT, id),
  /**
   * 工作空间「工具」删除触发器权限
   */
  triggerDelete: (id: string) => canRes(P.TOOL_TRIGGER_DELETE, id),

  // —— 文件夹 ——
  /**
   * 工作空间「工具」文件夹创建权限
   */
  folderCreate: (id: string) => canRes(P.TOOL_FOLDER_CREATE, id),
  /**
   * 工作空间「工具」文件夹查看权限
   */
  folderRead: (id: string) => canRes(P.TOOL_FOLDER_READ, id),
  /**
   * 工作空间「工具」文件夹编辑权限
   */
  folderEdit: (id: string) => canRes(P.TOOL_FOLDER_EDIT, id),
  /**
   * 工作空间「工具」文件夹删除权限
   */
  folderDelete: (id: string) => canRes(P.TOOL_FOLDER_DELETE, id),
  /**
   * 工作空间「工具」文件夹资源授权权限
   */
  folderAuth: (id: string) => canRes(P.TOOL_FOLDER_AUTH, id),
  folderManage: () => true,
}

export default workspace
