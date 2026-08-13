/** 系统「用户组」按钮权限。$perm.userGroup.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.SYSTEM_USER_GROUP_READ),
  create: () => canSys(P.SYSTEM_USER_GROUP_CREATE),
  edit: () => canSys(P.SYSTEM_USER_GROUP_EDIT),
  delete: () => canSys(P.SYSTEM_USER_GROUP_DELETE),
  addMember: () => canSys(P.SYSTEM_USER_GROUP_ADD_MEMBER),
  removeMember: () => canSys(P.SYSTEM_USER_GROUP_REMOVE_MEMBER),
}
