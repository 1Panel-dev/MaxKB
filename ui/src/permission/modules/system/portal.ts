/** 系统「门户访问设置」按钮权限。$perm.portal.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  /**
   * 系统「门户访问设置」只读权限
   */
  read: () => canSys(P.PORTAL_READ), edit: () => canSys(P.PORTAL_EDIT) }
