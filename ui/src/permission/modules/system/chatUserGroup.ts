/** 系统「对话用户组」按钮权限。$perm.chatUserGroup.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「对话用户组」只读权限
   */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_READ],Compare.OR),
  create: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_CREATE],Compare.OR),
  edit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_EDIT],Compare.OR),
  delete: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_DELETE],Compare.OR),
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_ADD_MEMBER],Compare.OR),
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.USER_GROUP_REMOVE_MEMBER],Compare.OR),
  authRead: () => canSys(P.CHAT_USER_AUTH_READ),
}
