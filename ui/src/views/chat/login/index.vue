<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { v4 as uuidv4 } from 'uuid'
import ChatAuthApi from '@/api/chat/auth'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { LOGIN_METHOD } from '@/api/enums'
import type { ApplicationAuthProfileMeta, LoginConfig, LoginMethod } from '@/api/types'
import { useStore } from '@/stores/chat'
import LoginModePanel from '@/views/login/components/LoginModePanel.vue'
import type { LoginService } from '@/views/login/types'

defineOptions({ name: 'ChatLogin' })

// 门户登录与单应用登录共用本页，场景由守卫切换到 Store 的当前认证场景
const route = useRoute()
const router = useRouter()
const { auth } = useStore()

const loginTitle = computed(() => {
  if (auth.isPortal) return '门户登录'
  return (auth.authProfile?.meta as ApplicationAuthProfileMeta | undefined)?.application_name || '登录'
})

// 认证前置配置只有可用登录方式，默认登录方式依次取本地、LDAP、第一个可用方式
const loginConfig = computed<LoginConfig>(() => {
  const loginMethods = auth.authProfile?.login_value?.length ? auth.authProfile.login_value : [LOGIN_METHOD.LOCAL]
  const defaultLoginMethod =
    [LOGIN_METHOD.LOCAL, LOGIN_METHOD.LDAP].find((method) => loginMethods.includes(method)) ?? loginMethods[0] ?? LOGIN_METHOD.LOCAL
  return { default_value: defaultLoginMethod, login_methods: loginMethods, max_attempts: auth.authProfile?.max_attempts ?? 1 }
})

/** 第三方认证回调后需要恢复的当前查询参数，如守卫记录的 redirect。 */
const getRouteQueryString = () => {
  const queryParams = new URLSearchParams()
  Object.entries(route.query).forEach(([key, value]) => {
    if (typeof value === 'string') queryParams.append(key, value)
  })
  return queryParams.toString()
}

// 回调地址携带 accessToken 和当前查询参数，后端据此回到对应应用的登录场景
const getExternalLoginUrl = (authType: LoginMethod): Promise<string> => {
  if (![LOGIN_METHOD.CAS, LOGIN_METHOD.OIDC, LOGIN_METHOD.OAUTH2].some((method) => method === authType)) return Promise.resolve('')

  return ChatAuthApi.getExternalAuthSetting(authType).then(({ config }) => {
    if (!config) return ''

    const { accessToken } = auth
    const queryString = getRouteQueryString()
    const callbackUrl = `${config.redirectUrl}${accessToken ? `/${accessToken}` : ''}${queryString ? `?${queryString}` : ''}`
    if (authType === LOGIN_METHOD.CAS) {
      if (!config.ldpUri) return ''
      const separator = config.ldpUri.includes('?') ? '&' : '?'
      return `${config.ldpUri}${separator}service=${encodeURIComponent(callbackUrl)}`
    }
    if (authType === LOGIN_METHOD.OIDC) {
      if (!config.authEndpoint || !config.clientId) return ''
      const scope = config.scope || 'openid+profile+email'
      let url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${callbackUrl}&response_type=code&scope=${scope}`
      if (config.state) url += `&state=${config.state}`
      return url
    }

    // OAuth2 通过 state 透传 accessToken
    if (!config.authEndpoint || !config.clientId) return ''
    const redirectUrl = `${config.redirectUrl}${queryString ? `&${queryString}` : ''}`
    const state = accessToken ? `${uuidv4()}_${accessToken}` : uuidv4()
    let url = `${config.authEndpoint}?client_id=${config.clientId}&response_type=code&redirect_uri=${redirectUrl}&state=${state}`
    if (config.scope) url += `&scope=${config.scope}`
    return url
  })
}

const getLarkRedirectUri = () => {
  const queryParams = new URLSearchParams(getRouteQueryString())
  if (auth.accessToken) queryParams.set('accessToken', auth.accessToken)
  const queryString = queryParams.toString()
  return `${window.location.origin}${CHAT_API_BASE_PATH}/auth/lark${queryString ? `?${queryString}` : ''}`
}

// 登录成功后回到守卫记录的原地址，没有时进入当前场景首页
const getRedirectRoute = (): RouteLocationRaw => {
  const { redirect } = route.query
  if (typeof redirect === 'string' && redirect.startsWith('/')) return redirect
  if (auth.accessToken) return { name: 'chat-home', params: { accessToken: auth.accessToken } }
  return { name: 'portal-home' }
}

const loginService: LoginService = {
  get rsaKey() {
    return auth.authProfile?.rsa_key ?? ''
  },
  login: (loginRequest) => auth.login(loginRequest),
  ldapLogin: (loginForm) => auth.ldapLogin(loginForm),
  // 验证码：后端按失败次数决定是否需要，无需时返回空字符串；目前仅应用场景支持
  getCaptcha: (username) => {
    const { accessToken } = auth
    if (!accessToken || !username.trim()) return Promise.resolve('')
    return ChatAuthApi.getCaptcha(username, accessToken).then(({ captcha }) => captcha)
  },
  getExternalLoginUrl,
  getQrCodeSources: () => ChatAuthApi.getQrCodeSources(),
  loginWithDingTalk: (authCode) => auth.loginWithDingTalk(authCode),
  get larkRedirectUri() {
    return getLarkRedirectUri()
  },
  get wecomState() {
    return auth.accessToken ?? ''
  },
  onLoginSuccess: () => router.replace(getRedirectRoute()),
}
</script>

<template>
  <div class="chat-login flex-center flex-col">
    <div class="mb-6 flex-col-center w-100 max-w-full gap-4">
      <img src="@/assets/mk-logo/MaxKB-logo.svg" alt="MaxKB" class="h-9" />
      <h2 class="max-w-full truncate" :title="loginTitle">{{ loginTitle }}</h2>
    </div>
    <el-card class="chat-login__card w-100">
      <LoginModePanel :login-config="loginConfig" :login-service="loginService" />
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.chat-login {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(var(--mk-primary-rgb) / 5%) 20%, rgba(var(--mk-primary-rgb) / 10%) 100%),
    var(--mk-N100);
  min-height: 100vh;
  padding: 16px;
}

.chat-login__card {
  --el-card-padding: 40px;
  border: none;
  height: 526px;
  max-width: 100%;
  position: relative;
}
</style>
