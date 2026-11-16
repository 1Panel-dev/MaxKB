/**
 * B 类：系统全局项按钮权限（扁平、单场景，无 workspace/share）。
 * 该对象会在 modules/index.ts 里被展开到顶层：$perm.user.* / $perm.role.* / ...
 */

import user from './user'
import workspace from './workspace'
import role from './role'
import userGroup from './userGroup'
import authorization from './authorization'
import chatUser from './chatUser'
import chatUserGroup from './chatUserGroup'
import chatAuth from './chatAuth'
import portal from './portal'
import loginAuth from './loginAuth'
import appearance from './appearance'
import email from './email'
import operationLog from './operationLog'
import homepage from './homepage'
import other from './other'
export default {
  /**
   * 系统「用户管理」按钮权限
   * */
  user,
  /**
   * 系统「工作空间」实体管理按钮权限
   * */
  workspace,
  /**
   * 系统「首页」按钮权限
   * */
  homepage,
  /**
   * 系统「角色管理」按钮权限
   * */
  role,
  /**
   * 系统「用户组」按钮权限
   * */
  userGroup,
  /**
   * 系统「资源授权」按钮权限（按资源类型分组）
   * */
  authorization,
  /**
   * 系统「对话用户」按钮权限
   */
  chatUser,
  /**
   * 系统「对话用户组」按钮权限
   */
  chatUserGroup,
  /**
   * 系统「对话用户认证」按钮权限
   */
  chatAuth,
  /**
   * 系统「门户访问设置」按钮权限
   */
  portal,
  /**
   * 系统「用户认证」按钮权限
   */
  loginAuth,
  /**
   * 系统「外观设置」按钮权限
   */
  appearance,
  /**
   * 系统「邮箱设置」按钮权限
   */
  email,
  /**
   * 系统「操作日志」按钮权限
   */
  operationLog,
  /**
   * 系统「其他」按钮权限
   */
  other
}
