/** 系统「角色管理」按钮权限。$perm.role.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「角色管理」只读权限
   * */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_READ],Compare.OR) && hasEdition(Edition.PE),
  /**
   * 系统「角色管理」创建权限
   */
  create: () => canSys(P.ROLE_CREATE),
  /**
   * 系统「角色管理」编辑权限
   */
  edit: () => canSys(P.ROLE_EDIT),
  /**
   * 系统「角色管理」删除权限
   */
  delete: () => canSys(P.ROLE_DELETE),
  /**
   * 系统「角色管理」添加成员权限
   */
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_ADD_MEMBER],Compare.OR),
  /**
   * 系统「角色管理」移除成员权限
   */
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ROLE_REMOVE_MEMBER],Compare.OR),
}
