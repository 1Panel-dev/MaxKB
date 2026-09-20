/** 「模型」各场景按钮权限：$perm.model.workspace.* / .system.* / .share.* */

import workspace from './workspace'
import system from './system'
import share from './share'

export default {
  workspace,
  /**
   * 系统「模型」权限
   * */
  system,
  /**
   * 系统「共享模型」权限
   * */
  share,
}
