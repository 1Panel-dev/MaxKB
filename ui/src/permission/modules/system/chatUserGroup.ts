/** 系统「对话用户组」按钮权限。$perm.chatUserGroup.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.USER_GROUP_READ),
  create: () => canSys(P.USER_GROUP_CREATE),
  edit: () => canSys(P.USER_GROUP_EDIT),
  delete: () => canSys(P.USER_GROUP_DELETE),
  addMember: () => canSys(P.USER_GROUP_ADD_MEMBER),
  removeMember: () => canSys(P.USER_GROUP_REMOVE_MEMBER),
  authRead: () => canSys(P.CHAT_USER_AUTH_READ),
}
