<script setup lang="ts">
import { computed, ref } from 'vue'
import { Grid, Monitor } from '@element-plus/icons-vue'
import LoginLayout from './components/LoginLayout.vue'
import AccountLogin from './modes/AccountLogin.vue'
import QrCodeLogin from './modes/QrCodeLogin.vue'
import { loginMethodLabels, qrCodeLoginMethods } from './constants'
import type { LoginConfig, LoginMethod, LoginMode, LoginOption, QrCodeProvider } from './types'

// TODO: 后期替换为登录配置接口返回的数据。
const loginConfig = ref<LoginConfig>({
  default_value: 'LOCAL',
  login_methods: ['SAML2', 'wecom', 'dingtalk', 'lark', 'OIDC', 'LDAP', 'OAuth2', 'CAS', 'LOCAL'],
})

const isQrCodeLoginMethod = (method: LoginMethod): method is QrCodeProvider =>
  qrCodeLoginMethods.includes(method as QrCodeProvider)

const loginMode = ref<LoginMode>(
  isQrCodeLoginMethod(loginConfig.value.default_value) ? 'qr-code' : 'account',
)

const normalLoginMethods = computed<LoginOption<LoginMethod>[]>(() =>
  loginConfig.value.login_methods
    .filter((method) => method !== 'LOCAL' && !isQrCodeLoginMethod(method))
    .map((method) => ({ label: loginMethodLabels[method], value: method })),
)

const qrCodeProviders = computed<LoginOption<QrCodeProvider>[]>(() =>
  loginConfig.value.login_methods.filter(isQrCodeLoginMethod).map((method) => ({
    label: loginMethodLabels[method],
    value: method,
  })),
)

const showLoginModeSwitch = computed(
  () => loginConfig.value.login_methods.includes('LOCAL') && qrCodeProviders.value.length > 0,
)

const toggleLoginMode = () => {
  loginMode.value = loginMode.value === 'account' ? 'qr-code' : 'account'
}
</script>

<template>
  <LoginLayout>
    <button
      v-if="showLoginModeSwitch"
      type="button"
      class="login-mode-switch"
      :aria-label="loginMode === 'account' ? '切换扫码登录' : '切换账号登录'"
      @click="toggleLoginMode"
    >
      <MkIcon :icon="loginMode === 'account' ? Grid : Monitor" :size="24" />
    </button>

    <AccountLogin v-if="loginMode === 'account'" :login-methods="normalLoginMethods" />
    <QrCodeLogin
      v-else-if="loginMode === 'qr-code'"
      :default-provider="loginConfig.default_value"
      :providers="qrCodeProviders"
      @change-mode="loginMode = $event"
    />
  </LoginLayout>
</template>

<style scoped>
.login-mode-switch {
  position: absolute;
  right: 12px;
  top: 12px;
  z-index: 1;
}
</style>
