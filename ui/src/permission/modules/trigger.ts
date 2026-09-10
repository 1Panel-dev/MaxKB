/** 工作空间触发器操作权限。 */
import { can } from '../policy'
import { PermissionConstants as P } from '../core'
export default {
  create: () => can(P.TRIGGER_CREATE),
  edit: () => can(P.TRIGGER_EDIT),
  delete: () => can(P.TRIGGER_DELETE),
}
