<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LoginService } from '../types'
import type { QrCodeConfig } from '@/api/types'

defineOptions({ name: 'WecomQrCode' })

const { locale, t } = useI18n({ useScope: 'global' })
const props = defineProps<{ config: QrCodeConfig; loginService: LoginService }>()

const iframeUrl = computed(() => {
  if (!props.config.qr_url || !props.config.callback_url) return ''
  const params = new URLSearchParams({
    agentid: props.config.agent_id ?? '',
    appid: props.config.corp_id ?? '',
    lang: locale.value === 'en-US' ? 'en' : 'zh',
    login_type: 'CorpApp',
    redirect_uri: props.config.callback_url,
    state: props.loginService.wecomState,
  })
  return `${props.config.qr_url}?${params}`
})
</script>

<template>
  <template v-if="iframeUrl">
    <div class="mt-6 mb-3 flex-center">
      <img src="@/assets/logo/logo_enterprise-wechat.svg" alt="" width="24px" class="mr-2" />
      <h2>{{ t('auth.qrCode.title', { provider: t('auth.methods.wecom') }) }}</h2>
    </div>
    <div class="wecom-qr-layout">
      <iframe :src="iframeUrl" class="h-90 w-full" scrolling="no" />
    </div>
  </template>
</template>

<style scoped lang="scss">
.wecom-qr-layout {
  // 将内部 192px 的码图放大到 200px，外框高度与顶部裁切偏移同步缩放。
  --wecom-qr-scale: calc(200 / 192);
  height: calc(280px * var(--wecom-qr-scale));
  overflow: hidden;

  iframe {
    display: block;
    position: relative;
    top: calc(-104px * var(--wecom-qr-scale));
    transform: scale(var(--wecom-qr-scale));
    transform-origin: top center;
  }
}
</style>
