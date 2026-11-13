import { LOGIN_METHOD } from '@/api/enums'
import type { LoginMethod, QrCodeProvider } from '@/api/types'

export const qrCodeLoginMethods: QrCodeProvider[] = [LOGIN_METHOD.WECOM, LOGIN_METHOD.DINGTALK, LOGIN_METHOD.LARK]

/** 登录界面的方式标签；接口值保持不变。 */
export const LOGIN_METHOD_LABEL_KEYS = {
  [LOGIN_METHOD.LOCAL]: 'auth.login.options.local',
  [LOGIN_METHOD.LDAP]: 'auth.login.options.ldap',
  [LOGIN_METHOD.CAS]: 'auth.login.options.cas',
  [LOGIN_METHOD.OIDC]: 'auth.login.options.oidc',
  [LOGIN_METHOD.OAUTH2]: 'auth.login.options.oauth2',
  [LOGIN_METHOD.SAML2]: 'auth.login.options.saml2',
  [LOGIN_METHOD.DINGTALK]: 'auth.login.options.dingtalk',
  [LOGIN_METHOD.LARK]: 'auth.login.options.lark',
  [LOGIN_METHOD.WECOM]: 'auth.login.options.wecom',
} as const satisfies Record<LoginMethod, string>
