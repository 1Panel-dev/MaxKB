<script setup lang="ts">
import { nextTick, onBeforeUnmount, watch } from 'vue'
import type { QrCodeConfig } from '@/api/types'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '@/utils/script-loader'

defineOptions({ name: 'LarkQrCode' })

const props = defineProps<{ config: QrCodeConfig }>()
let messageHandler: ((event: MessageEvent) => void) | undefined

const initialize = async () => {
  if (!props.config.app_key) return
  await loadLoginScript('https://lf-package-cn.feishucdn.com/obj/feishu-static/lark/passport/qrcode/LarkSSOSDKWebQRCode-1.0.3.js', 'lark-login-sdk')
  await nextTick()
  if (!window.QRLogin) throw new Error('飞书扫码 SDK 加载失败')

  const adminPrefix = window.MaxKB?.prefix ?? import.meta.env.VITE_BASE_PATH ?? '/admin/'
  const authorizeUrl = new URL('https://passport.feishu.cn/suite/passport/oauth/authorize')
  authorizeUrl.search = new URLSearchParams({
    client_id: props.config.app_key,
    redirect_uri: `${window.location.origin}${adminPrefix.replace(/\/$/, '')}/api/lark`,
    response_type: 'code',
    state: 'fit2cloud-lark-qr',
  }).toString()
  const qrLogin = window.QRLogin({ goto: authorizeUrl.toString(), height: '266', id: 'lark-qr-code', style: 'width:280px;height:280px;margin:0 auto;', width: '266' })

  if (messageHandler) window.removeEventListener('message', messageHandler)
  messageHandler = (event) => {
    if (!qrLogin.matchOrigin(event.origin) || !qrLogin.matchData(event.data)) return
    const temporaryCode = (event.data as { tmp_code?: string }).tmp_code
    if (temporaryCode) window.location.href = `${authorizeUrl}&tmp_code=${temporaryCode}`
  }
  window.addEventListener('message', messageHandler)
}

watch(
  () => props.config,
  () => void initialize().catch((error: unknown) => MsgError(String(error))),
  { immediate: true },
)

onBeforeUnmount(() => {
  if (messageHandler) window.removeEventListener('message', messageHandler)
})
</script>

<template>
  <div class="mt-6 flex-center">
    <img src="@/assets/logo/logo_lark.svg" alt="" width="24px" class="mr-2" />
    <h2>飞书扫码登录</h2>
  </div>
  <div id="lark-qr-code" />
</template>
