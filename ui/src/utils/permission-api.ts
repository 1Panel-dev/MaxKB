import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import roleSystemApi from '@/api/system/role'
import roleWorkspaceApi from '@/api/workspace/role'

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
  if (hasPermission([EditionConst.IS_EE, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole], 'AND')) {
    // 加载企业版工作空间管理员 API
    return workspaceApiMap[type]
  } else {
    // 加载系统管理员 API
    return systemApiMap[type]
  }
}
