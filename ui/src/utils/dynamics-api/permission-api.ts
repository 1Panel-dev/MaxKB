import {PermissionConst, EditionConst, RoleConst} from '@/utils/permission/data'
import {hasPermission} from '@/utils/permission/index'
import roleSystemApi from '@/api/system/role'
import roleWorkspaceApi from '@/api/workspace/role'
import systemWorkspaceApi from '@/api/system/workspace'
import workspaceApi from '@/api/workspace/workspace'
import systemChatUserApi from '@/api/system/chat-user'
import workspaceChatUserApi from '@/api/workspace/chat-user'
import systemUserGroupApi from '@/api/system/user-group'
import workspaceUserGroupApi from '@/api/workspace/user-group'
import {ComplexPermission} from '../permission/type'

// 系统管理员 API
const systemApiMap = {
  role: roleSystemApi,
  workspace: systemWorkspaceApi,
  chatUser: systemChatUserApi,
  userGroup: systemUserGroupApi
} as any

// 企业版工作空间管理员 API
const workspaceApiMap = {
  role: roleWorkspaceApi,
  workspace: workspaceApi,
  chatUser: workspaceChatUserApi,
  userGroup: workspaceUserGroupApi
} as any

/** 动态导入 API 模块的函数
 *  loadPermissionApi('role')
 */

export function loadPermissionApi(type: string) {
  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    if (hasPermission([RoleConst.ADMIN, RoleConst.EXTENDS_ADMIN], 'OR')) {
      // 加载系统管理员 API
      return systemApiMap[type]
    } else if (hasPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.EXTENDS_WORKSPACE_MANAGE.getWorkspaceRole], 'OR')) {
      // 加载企业版工作空间管理员 API
      return workspaceApiMap[type]
    }
  }
}
