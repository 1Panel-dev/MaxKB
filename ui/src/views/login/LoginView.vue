<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseInfoApi from '@/api/admin/auth/base-info.ts'
import { useStore } from '@/stores'
import type { LoginConfig, QrCodeProvider } from '@/types'
import LoginLayout from './components/LoginLayout.vue'
import AccountLogin from './modes/AccountLogin.vue'
import QrCodeLogin from './modes/QrCodeLogin.vue'
import { qrCodeLoginMethods } from './constants'
import { loadLoginScript } from '@/utils/script-loader.ts'

const route = useRoute()
const router = useRouter()
const { login, profile, theme } = useStore()
const isLoading = ref(true)
const rsaPublicKey = computed(() => profile.BaseProfile?.rsa ?? '')
const loginConfig = ref<LoginConfig>({
  default_value: 'LOCAL',
  login_methods: ['LOCAL'],
  max_attempts: 1,
})
const loginMode = ref<'account' | 'qr-code'>('account')

const qrCodeProviders = computed(() =>
  (loginConfig.value.login_methods ?? []).filter((method): method is QrCodeProvider =>
    qrCodeLoginMethods.includes(method as QrCodeProvider),
  ),
)
const showLoginModeSwitch = computed(
  () =>
    (loginConfig.value.login_methods ?? []).includes('LOCAL') && qrCodeProviders.value.length > 0,
)

const completeClientLogin = async () => {
  const client = typeof route.query.client === 'string' ? route.query.client : ''
  if (client === 'dingtalk' && typeof route.query.corpId === 'string') {
    const dingTalkSdk = await import('dingtalk-jsapi')
    const result = await dingTalkSdk.runtime.permission.requestAuthCode({
      corpId: route.query.corpId,
    })
    await login.asyncLoginWithDingTalk(result.code, true)
  } else if (client === 'lark' && typeof route.query.appId === 'string') {
    await loadLoginScript(
      'https://lf-scm-cn.feishucdn.com/lark/op/h5-js-sdk-1.5.35.js',
      'lark-client-sdk',
    )
    if (!window.tt) throw new Error('飞书客户端 SDK 加载失败')
    const code = await new Promise<string>((resolve, reject) => {
      window.tt?.requestAuthCode({
        appId: route.query.appId as string,
        success: (result) => resolve(result.code),
        fail: reject,
      })
    })
    await login.asyncLoginWithLark(code)
  } else {
    return
  }
  await router.push({ name: 'workspace-home', params: { workspaceId: 'default' } })
}

onBeforeMount(() => {
  isLoading.value = true
  profile.loadBaseProfile().then(() => {
    // 企业版和专业版：第三方登录
    if (profile.isPE || profile.isEE) {
      const loginConfigRequest = BaseInfoApi.getLoginConfig()
      const themeRequest = theme.loadThemeInfo()
      return Promise.all([themeRequest, loginConfigRequest])
    }
  })
})
</script>

<template>
  <LoginLayout v-loading="isLoading">
    <el-button
      v-if="showLoginModeSwitch"
      type="primary"
      text
      class="login-mode-switch"
      :aria-label="loginMode === 'account' ? '切换扫码登录' : '切换账号登录'"
      @click="loginMode = loginMode === 'account' ? 'qr-code' : 'account'"
    >
      <MkIcon
        :name="loginMode === 'account' ? 'icon_qr_outlined' : 'icon_pc_outlined'"
        :size="48"
      />
    </el-button>

    <AccountLogin
      v-if="loginMode === 'account'"
      :login-config="loginConfig"
      :rsa-public-key="rsaPublicKey"
    />
    <QrCodeLogin v-else :login-config="loginConfig" />
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
