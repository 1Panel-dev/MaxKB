/** 「工具」各场景按钮权限：$perm.tool.workspace.* / .system.* / .share.* */

import workspace from './workspace'
import system from './system'
import share from './share'
import workspaceShared from './workspace-shared'

export default {
  /**工作空间「工具」权限
   * */
  workspace,
  /**
   * 系统「工具」权限
   * */
  system,
  /**系统「共享工具」权限
   * */
  share,
  /**工作空间「共享工具」权限
   * */
  workspaceShared
}
