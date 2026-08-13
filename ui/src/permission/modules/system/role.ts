/** 系统「角色管理」按钮权限。$perm.role.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.ROLE_READ),
  create: () => canSys(P.ROLE_CREATE),
  edit: () => canSys(P.ROLE_EDIT),
  delete: () => canSys(P.ROLE_DELETE),
  addMember: () => canSys(P.ROLE_ADD_MEMBER),
  removeMember: () => canSys(P.ROLE_REMOVE_MEMBER),
}
