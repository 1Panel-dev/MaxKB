/** 系统「首页」按钮权限 → $perm.homepage.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default { read: () => canSys(P.HOMEPAGE_READ), export: () => canSys(P.HOMEPAGE_EXPORT) }
