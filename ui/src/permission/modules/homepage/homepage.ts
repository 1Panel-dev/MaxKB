/** 工作空间「概览」按钮权限。* */

import { PermissionConstants as P } from '../../core'
import { can } from '../../policy'

export default {
  /**
   * 工作空间「概览」只读权限
   */
  read: () => can(P.HOMEPAGE_READ),
  /**
   * 工作空间「概览」导出权限
   */
  export: () => can(P.HOMEPAGE_EXPORT)
}
