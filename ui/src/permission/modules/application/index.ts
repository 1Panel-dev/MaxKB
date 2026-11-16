/** 「应用」在各场景下的按钮权限。调用侧显式选择场景：$perm.application.workspace.* / $perm.application.system.* */

import system from './system'
import workspace from './workspace'

export default {
 /**
 * 工作空间「智能体」权限
 */
  workspace,
  /**
   * 系统「智能体」权限
   * */
  system }
