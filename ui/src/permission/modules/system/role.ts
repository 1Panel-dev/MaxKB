/** 系统「角色管理」按钮权限。$perm.role.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「角色管理」只读权限
   * */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_READ],Compare.OR) && hasEdition(Edition.PE),
  create: () => canSys(P.ROLE_CREATE),
  edit: () => canSys(P.ROLE_EDIT),
  delete: () => canSys(P.ROLE_DELETE),
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_ADD_MEMBER],Compare.OR),
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_REMOVE_MEMBER],Compare.OR),
}
