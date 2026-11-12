/** 工作空间「概览」按钮权限。* */

import { can } from '../../policy'
import { PermissionConstants as P } from '../../core'

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
