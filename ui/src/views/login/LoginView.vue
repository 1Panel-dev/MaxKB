<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'
import BaseInfoApi from '@/api/admin/auth/base-info.ts'
import { useStore } from '@/stores'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig, QrCodeProvider } from '@/api/types'
import LoginLayout from './components/LoginLayout.vue'
import AccountLogin from './modes/AccountLogin.vue'
import QrCodeLogin from './modes/QrCodeLogin.vue'
import { qrCodeLoginMethods } from './constants'

const { auth } = useStore()

const isLoading = ref(true)
const loginConfig = ref<LoginConfig>({ default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL], max_attempts: 1 })
const loginMode = ref<'account' | 'qr-code'>('account')

const qrCodeProviders = computed(() =>
  (loginConfig.value.login_methods ?? []).filter((method): method is QrCodeProvider => qrCodeLoginMethods.includes(method as QrCodeProvider)),
)
const accountLoginMethods = computed(() =>
  (loginConfig.value.login_methods ?? []).filter((method) => !qrCodeLoginMethods.includes(method as QrCodeProvider)),
)
const accountLoginConfig = computed<LoginConfig>(() => ({
  ...loginConfig.value,
  default_value: qrCodeLoginMethods.includes(loginConfig.value.default_value as QrCodeProvider)
    ? LOGIN_METHOD.LOCAL
    : loginConfig.value.default_value,
  login_methods: accountLoginMethods.value,
}))
const qrCodeLoginConfig = computed<LoginConfig>(() => ({
  ...loginConfig.value,
  default_value: qrCodeLoginMethods.includes(loginConfig.value.default_value as QrCodeProvider)
    ? loginConfig.value.default_value
    : LOGIN_METHOD.WECOM,
  login_methods: qrCodeProviders.value,
}))
const showLoginModeSwitch = computed(() => accountLoginMethods.value.length > 0 && qrCodeProviders.value.length > 0)

onBeforeMount(() => {
  isLoading.value = true
  auth
    .loadPlatformProfile()
    .then(() => {
      if (auth.isPE || auth.isEE) {
        return BaseInfoApi.getLoginConfig().then((config) => {
          if (Object.keys(config).length > 0) {
            loginConfig.value = config
          } else {
            loginConfig.value = { max_attempts: 1, default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL] }
          }
        })
      }
      loginConfig.value = { max_attempts: 1, default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL] }
    })
    .finally(() => {
      isLoading.value = false
    })
})
</script>

<template>
  <LoginLayout v-if="!isLoading">
    <el-button
      v-if="showLoginModeSwitch"
      type="primary"
      text
      class="login-mode-switch"
      :aria-label="loginMode === 'account' ? '切换扫码登录' : '切换账号登录'"
      @click="loginMode = loginMode === 'account' ? 'qr-code' : 'account'"
    >
      <MkIcon :name="loginMode === 'account' ? 'icon_qr_outlined' : 'icon_pc_outlined'" :size="48" />
    </el-button>

    <AccountLogin v-if="loginMode === 'account'" :login-config="accountLoginConfig" />
    <QrCodeLogin v-else :login-config="qrCodeLoginConfig" />
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
