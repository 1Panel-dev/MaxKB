/** 系统「首页」按钮权限 → $perm.homepage.* */

import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「首页」只读权限
   */
  read: () => hasPermission([RoleConstants.ADMIN,P.HOMEPAGE_READ],Compare.OR),
  export: () => hasPermission([RoleConstants.ADMIN,P.HOMEPAGE_EXPORT],Compare.OR)
}
