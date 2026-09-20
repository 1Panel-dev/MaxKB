/** 系统「邮箱设置」按钮权限。$perm.email.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  /**
   * 系统「邮箱设置」只读权限
   */
  read: () => canSys(P.EMAIL_SETTING_READ), edit: () => canSys(P.EMAIL_SETTING_EDIT) }
