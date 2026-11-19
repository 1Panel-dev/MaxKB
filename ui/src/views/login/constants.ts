import type { QrCodeProvider } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'

export const qrCodeLoginMethods: QrCodeProvider[] = [LOGIN_METHOD.WECOM, LOGIN_METHOD.DINGTALK, LOGIN_METHOD.LARK]
