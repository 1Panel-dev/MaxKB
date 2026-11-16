/** 系统「首页」按钮权限 → $perm.homepage.* */

import { Compare, PermissionConstants as P, RoleConstants, hasEdition, hasPermission } from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「首页」只读权限
   */
  read: () => hasPermission([RoleConstants.ADMIN,P.SYSTEM_HOMEPAGE_READ],Compare.OR) && hasEdition(Edition.EE),
  export: () => hasPermission([RoleConstants.ADMIN,P.SYSTEM_HOMEPAGE_EXPORT],Compare.OR)
}
