<script setup lang="ts">
import { computed, ref } from 'vue'
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
    <el-button
      v-if="showLoginModeSwitch"
      type="primary"
      text
      class="login-mode-switch"
      :aria-label="loginMode === 'account' ? '切换扫码登录' : '切换账号登录'"
      @click="toggleLoginMode"
    >
      <MkIcon
        :name="loginMode === 'account' ? 'icon_qr_outlined' : 'icon_pc_outlined'"
        :size="48"
      />
    </el-button>

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
  border-radius: 0 12px 0 0;
  height: 70px;
  margin: 0;
  overflow: hidden;
  padding: 0;
  position: absolute;
  right: 0;
  top: 0;
  width: 70px;
  z-index: 1;
  .el-icon {
    top: -6px;
    right: -6px;
  }

  &::after {
    background: var(--el-color-white);
    clip-path: polygon(0 0, 0 100%, 100% 100%);
    content: '';
    inset: 0;
    opacity: 1;
    position: absolute;
    transition: opacity 0.2s;
  }
}
</style>
