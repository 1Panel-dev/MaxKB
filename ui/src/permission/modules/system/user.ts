/** 系统「用户管理」按钮权限。$perm.user.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.USER_READ),
  create: () => canSys(P.USER_CREATE),
  edit: () => canSys(P.USER_EDIT),
  delete: () => canSys(P.USER_DELETE),
  setRole: () => canSys(P.USER_SET_ROLE),
  import: () => canSys(P.USER_IMPORT),
}
