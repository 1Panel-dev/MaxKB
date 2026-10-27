/** 账号登录与扫码登录组件在 Admin、Chat 入口间的差异，由登录页面通过 LoginService 提供。 */

import type { LoginMethod, QrCodeSource } from '@/api/types'

export interface AccountLoginForm {
  captcha: string
  password: string
  username: string
}

export interface LoginService {
  /** 本地账号登录使用的 RSA 公钥。 */
  rsaKey: string
  /** 本地账号登录，表单已加密。 */
  login: (loginRequest: { encryptedData: string; username: string }) => Promise<unknown>
  ldapLogin: (loginForm: AccountLoginForm) => Promise<unknown>
  /** 获取本地账号登录验证码；无需验证码时返回空字符串。 */
  getCaptcha: (username: string) => Promise<string>
  /** 生成 CAS、OIDC、OAuth2、SAML2 等第三方认证的跳转地址；配置不完整时返回空字符串。 */
  getExternalLoginUrl: (method: LoginMethod) => Promise<string>
  getQrCodeSources: () => Promise<QrCodeSource[]>
  loginWithDingTalk: (authCode: string) => Promise<unknown>
  /** 飞书扫码授权后的后端回调地址。 */
  larkRedirectUri: string
  /** 企业微信扫码透传给后端回调的 state。 */
  wecomState: string
  /** 登录成功后的跳转，账号与扫码登录共用。 */
  onLoginSuccess: () => unknown
  /** 不提供时不显示“忘记密码”入口。 */
  forgotPassword?: () => void
}
