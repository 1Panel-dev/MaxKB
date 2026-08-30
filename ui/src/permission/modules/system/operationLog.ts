/** 系统「操作日志」按钮权限。$perm.operationLog.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default { read: () => canSys(P.OPERATION_LOG_READ), export: () => canSys(P.OPERATION_LOG_EXPORT), clearPolicy: () => canSys(P.OPERATION_LOG_CLEAR_POLICY) }
