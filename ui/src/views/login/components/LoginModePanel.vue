<script setup lang="ts">
import { computed, ref } from 'vue'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig, QrCodeProvider } from '@/api/types'
import AccountLogin from '../modes/AccountLogin.vue'
import QrCodeLogin from '../modes/QrCodeLogin.vue'
import { qrCodeLoginMethods } from '../constants'
import type { LoginService } from '../types'

defineOptions({ name: 'LoginModePanel' })

// 按登录配置拆分账号登录与扫码登录，默认登录方式决定初始模式；配置加载完成后再挂载
const props = defineProps<{ loginConfig: LoginConfig; loginService: LoginService }>()

const isQrCodeMethod = (method: string) => qrCodeLoginMethods.includes(method as QrCodeProvider)

const loginMode = ref<'account' | 'qr-code'>(isQrCodeMethod(props.loginConfig.default_value) ? 'qr-code' : 'account')

const qrCodeProviders = computed(() => (props.loginConfig.login_methods ?? []).filter((method): method is QrCodeProvider => isQrCodeMethod(method)))
const accountLoginMethods = computed(() => (props.loginConfig.login_methods ?? []).filter((method) => !isQrCodeMethod(method)))
const accountLoginConfig = computed<LoginConfig>(() => ({
  ...props.loginConfig,
  default_value: isQrCodeMethod(props.loginConfig.default_value)
    ? (accountLoginMethods.value[0] ?? LOGIN_METHOD.LOCAL)
    : props.loginConfig.default_value,
  login_methods: accountLoginMethods.value,
}))
const qrCodeLoginConfig = computed<LoginConfig>(() => ({
  ...props.loginConfig,
  default_value: isQrCodeMethod(props.loginConfig.default_value) ? props.loginConfig.default_value : (qrCodeProviders.value[0] ?? LOGIN_METHOD.WECOM),
  login_methods: qrCodeProviders.value,
}))
const showLoginModeSwitch = computed(() => accountLoginMethods.value.length > 0 && qrCodeProviders.value.length > 0)
</script>

<template>
  <!-- 切换扫码登录或账号登录 -->
  <el-button
    v-if="showLoginModeSwitch"
    type="primary"
    text
    class="login-mode-switch"
    @click="loginMode = loginMode === 'account' ? 'qr-code' : 'account'"
  >
    <MkIcon :name="loginMode === 'account' ? 'icon_qr_outlined' : 'icon_pc_outlined'" :size="48" />
  </el-button>

  <AccountLogin v-if="loginMode === 'account'" :login-config="accountLoginConfig" :login-service="loginService" />
  <QrCodeLogin v-else :login-config="qrCodeLoginConfig" :login-service="loginService" />
</template>

<style scoped lang="scss">
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
