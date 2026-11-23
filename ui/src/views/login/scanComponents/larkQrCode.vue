<script setup lang="ts">
import { nextTick, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LoginService } from '../types'
import type { QrCodeConfig } from '@/api/types'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '@/utils/script-loader'

defineOptions({ name: 'LarkQrCode' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ config: QrCodeConfig; loginService: LoginService }>()
let messageHandler: ((event: MessageEvent) => void) | undefined

const initialize = async () => {
  if (!props.config.app_key) return
  await loadLoginScript('https://lf-package-cn.feishucdn.com/obj/feishu-static/lark/passport/qrcode/LarkSSOSDKWebQRCode-1.0.3.js', 'lark-login-sdk')
  await nextTick()
  if (!window.QRLogin) throw new Error(t('auth.qrCode.messages.sdkLoadFailed', { provider: t('auth.methods.lark') }))

  const authorizeUrl = new URL('https://passport.feishu.cn/suite/passport/oauth/authorize')
  authorizeUrl.search = new URLSearchParams({
    client_id: props.config.app_key,
    redirect_uri: props.loginService.larkRedirectUri,
    response_type: 'code',
    state: 'fit2cloud-lark-qr',
  }).toString()
  const qrLogin = window.QRLogin({
    goto: authorizeUrl.toString(),
    height: '280',
    id: 'lark-qr-code',
    width: '280',
  })

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
  <div class="mt-6 mb-3 flex-center">
    <img src="@/assets/logo/logo_lark.svg" alt="" width="24px" class="mr-2" />
    <h2>{{ t('auth.qrCode.title', { provider: t('auth.methods.lark') }) }}</h2>
  </div>
  <div id="lark-qr-code" class="lark-qr-layout mx-auto w-70" />
</template>

<style scoped lang="scss">
.lark-qr-layout {
  // 扣除飞书 iframe 内部顶部 28px 留白，标题间距由外层 mb-3 保持为 12px。
  :deep(iframe) {
    display: block;
    position: relative;
    top: -15px;
  }
}
</style>
