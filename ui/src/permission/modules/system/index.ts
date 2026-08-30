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

export default { user, workspace, role, userGroup, authorization, chatUser, chatUserGroup, chatAuth, portal, loginAuth, appearance, email, operationLog }
