/** Admin 登录页与外观设置登录预览使用的登录服务，对接 Admin 认证接口与 Store。 */

import { useRouter } from 'vue-router'
import { v4 as uuidv4 } from 'uuid'
import ExternalLoginApi from '@/api/admin/auth/external-login'
import LoginApi from '@/api/admin/auth/login'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginMethod } from '@/api/types'
import { useStore } from '@/stores'
import type { LoginService } from './types'

const getExternalLoginUrl = (authType: LoginMethod): Promise<string> => {
  if (authType === LOGIN_METHOD.SAML2) return ExternalLoginApi.getSamlLoginUrl()

  return ExternalLoginApi.getExternalAuthSetting(authType).then(({ config }) => {
    if (!config) return ''

    const redirectUrl = `${config.redirectUrl}`
    if (authType === LOGIN_METHOD.CAS) {
      if (!config.ldpUri) return ''
      const separator = config.ldpUri.includes('?') ? '&' : '?'
      return `${config.ldpUri}${separator}service=${encodeURIComponent(redirectUrl)}`
    }
    if (authType === LOGIN_METHOD.OIDC) {
      if (!config.authEndpoint || !config.clientId) return ''
      const scope = config.scope || 'openid+profile+email'
      let url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`
      if (config.state) url += `&state=${config.state}`
      return url
    }
    if (authType === LOGIN_METHOD.OAUTH2) {
      if (!config.authEndpoint || !config.clientId) return ''
      let url = `${config.authEndpoint}?client_id=${config.clientId}&response_type=code&redirect_uri=${redirectUrl}&state=${uuidv4()}`
      if (config.scope) url += `&scope=${config.scope}`
      return url
    }

    return ''
  })
}

export function useAdminLoginService(): LoginService {
  const router = useRouter()
  const { auth } = useStore()

  return {
    get rsaKey() {
      return auth.baseProfile?.rsa ?? ''
    },
    login: (loginRequest) => auth.asyncLogin(loginRequest),
    ldapLogin: (loginForm) => auth.asyncLdapLogin(loginForm),
    getCaptcha: (username) => LoginApi.getCaptcha(username).then(({ captcha }) => captcha),
    getExternalLoginUrl,
    getQrCodeSources: () => ExternalLoginApi.getQrCodeSources(),
    loginWithDingTalk: (authCode) => auth.asyncLoginWithDingTalk(authCode),
    larkRedirectUri: `${window.location.origin}${ADMIN_API_BASE_PATH}/lark`,
    wecomState: 'fit2cloud-wecom-qr',
    onLoginSuccess: () => router.push({ name: 'workspace-home', params: { workspaceId: 'default' } }),
    forgotPassword: () => void router.push({ name: 'forgot-password' }),
  }
}
