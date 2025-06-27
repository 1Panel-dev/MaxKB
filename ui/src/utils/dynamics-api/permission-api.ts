import {PermissionConst, EditionConst, RoleConst} from '@/utils/permission/data'
import {hasPermission} from '@/utils/permission/index'
import roleSystemApi from '@/api/system/role'
import roleWorkspaceApi from '@/api/workspace/role'
import {ComplexPermission} from '../permission/type'

// 系统管理员 API
const systemApiMap = {
  role: roleSystemApi,
} as any

// 企业版工作空间管理员 API
const workspaceApiMap = {
  role: roleWorkspaceApi,
} as any

/** 动态导入 API 模块的函数
 *  loadPermissionApi('role')
 */

export function loadPermissionApi(type: string) {
  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    if (hasPermission(new ComplexPermission(
      [RoleConst.ADMIN],
      [PermissionConst.ROLE_READ],
      [],
      'OR'), 'OR')) {
      // 加载系统管理员 API
      return systemApiMap[type]
    }
    if (hasPermission(new ComplexPermission(
      [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
      [PermissionConst.WORKSPACE_ROLE_READ.getWorkspacePermissionWorkspaceManageRole],
      [],
      'OR'), 'OR')) {
      // 加载企业版工作空间管理员 API
      return workspaceApiMap[type]
    }
  }
}
