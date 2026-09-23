/** 工作空间触发器操作权限。 */
import { can } from '../policy'
import { PermissionConstants as P } from '../core'
export default {
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
