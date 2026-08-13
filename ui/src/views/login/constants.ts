import { LOGIN_METHOD, type QrCodeProvider } from '@/api/types'

export const qrCodeLoginMethods: QrCodeProvider[] = [
  LOGIN_METHOD.WECOM,
  LOGIN_METHOD.DINGTALK,
  LOGIN_METHOD.LARK,
]
