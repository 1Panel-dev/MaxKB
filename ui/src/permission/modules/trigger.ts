/** 工作空间触发器操作权限。 */
import { can } from '../policy'
import { hasPermission, PermissionConstants as P } from '../core'
import { AggregatePermission, Role, RoleConstants } from '../core/common'
import { getWorkspaceId } from '@/utils/resource-context'
export default {
    /**
   * 工作空间「触发器」只读权限
   */
  read: () => {
    const workspaceId=getWorkspaceId() || ''
    return hasPermission(AggregatePermission.builder()
    .addRole(new Role(RoleConstants.WORKSPACE_MANAGE.name, workspaceId))
    .addPermission(P.TRIGGER_READ.getWorkspacePermission()({'workspaceId':workspaceId})).build())
  },
  /**
   * 工作空间「触发器」创建权限
   */
  create: () => can(P.TRIGGER_CREATE),
  /**
   * 工作空间「触发器」编辑权限
   */
  edit: () => can(P.TRIGGER_EDIT),
  /**
   * 工作空间「触发器」删除权限
   */
  delete: () => can(P.TRIGGER_DELETE),
  /**
   * 工作空间「触发器」查看执行记录权限
   */
  record: () => can(P.TRIGGER_RECORD)
}
