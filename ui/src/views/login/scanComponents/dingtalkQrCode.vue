<script setup lang="ts">
import { nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LoginService } from '../types'
import type { QrCodeConfig } from '@/api/types'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '@/utils/script-loader'

defineOptions({ name: 'DingTalkQrCode' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ config: QrCodeConfig; loginService: LoginService }>()

const initialize = async () => {
  if (!props.config.app_key || !props.config.corp_id) return
  await loadLoginScript('https://g.alicdn.com/dingding/h5-dingtalk-login/0.21.0/ddlogin.js', 'dingtalk-login-sdk')
  await nextTick()
  if (!window.DTFrameLogin) throw new Error(t('auth.qrCode.messages.sdkLoadFailed', { provider: t('auth.methods.dingtalk') }))
  window.DTFrameLogin(
    { id: 'dingtalk-qr-code', width: 280, height: 280 },
    {
      client_id: props.config.app_key,
      corpId: props.config.corp_id,
      prompt: 'consent',
      redirect_uri: encodeURIComponent(window.location.origin),
      response_type: 'code',
      scope: 'openid corpid',
      state: 'fit2cloud-ding-qr',
    },
    async ({ authCode }) => {
      await props.loginService.loginWithDingTalk(authCode)
      await props.loginService.onLoginSuccess()
    },
    MsgError,
  )
}

watch(
  () => props.config,
  () => void initialize().catch((error: unknown) => MsgError(String(error))),
  { immediate: true },
)
</script>

<template>
  <div class="relative z-10 mt-6 mb-3 flex-center">
    <img src="@/assets/logo/logo_dingtalk.svg" alt="" width="24px" class="mr-2" />
    <h2>{{ t('auth.qrCode.title', { provider: t('auth.methods.dingtalk') }) }}</h2>
  </div>
  <div class="ding-talk-layout">
    <div id="dingtalk-qr-code" />
  </div>
  <p class="relative mt-3 text-center text-N600">
    {{ t('auth.qrCode.scanHint', { provider: t('auth.methods.dingtalk') }) }}
  </p>
</template>
<style lang="scss" scoped>
.ding-talk-layout {
  // 当前 SDK 的二维码外框距 iframe 顶部约 40px，缩放后扣除该留白，外框距标题约 12px。
  // 扣除 iframe 底部约 40px 的留白，让下方提示与二维码外框保持约 12px 间距。
  height: calc((280px - 40px) * 7 / 6);
  margin: -48px auto 0;
  width: 280px;

  :deep(iframe) {
    display: block;
    transform: scale(calc(7 / 6));
    transform-origin: top center;
  }
}
</style>
