/** 系统「操作日志」按钮权限。$perm.operationLog.* */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「操作日志」只读权限
   */
  read: () => canSys(P.OPERATION_LOG_READ) && hasEdition(Edition.PE),
  export: () => canSys(P.OPERATION_LOG_EXPORT), clearPolicy: () => canSys(P.OPERATION_LOG_CLEAR_POLICY) }
