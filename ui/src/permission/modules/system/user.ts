/** 系统「用户管理」按钮权限。$perm.user.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  /**
   * 系统「用户管理」只读权限
   * */
  read: () => canSys(P.USER_READ),
  /**
   * 系统「用户管理」创建权限
   */
  create: () => canSys(P.USER_CREATE),
  /**
   * 系统「用户管理」编辑权限
   */
  edit: () => canSys(P.USER_EDIT),
  /**
   * 系统「用户管理」删除权限
   */
  delete: () => canSys(P.USER_DELETE),
  /**
   * 系统「用户管理」设置角色权限
   */
  setRole: () => canSys(P.USER_SET_ROLE),
  /**
   * 系统「用户管理」导入权限
   */
  import: () => canSys(P.USER_IMPORT),
}
