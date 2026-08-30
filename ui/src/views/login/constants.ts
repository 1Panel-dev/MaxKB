import { LOGIN_METHOD } from '@/api/enums'
import type { QrCodeProvider } from '@/api/types'

export const qrCodeLoginMethods: QrCodeProvider[] = [LOGIN_METHOD.WECOM, LOGIN_METHOD.DINGTALK, LOGIN_METHOD.LARK]
