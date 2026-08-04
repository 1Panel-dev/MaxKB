<script setup lang="ts">
import { computed } from 'vue'
import type { QrCodeConfig } from '@/api/admin/auth/types'

defineOptions({ name: 'WecomQrCode' })

const props = defineProps<{ config: QrCodeConfig }>()

const iframeUrl = computed(() => {
  if (!props.config.qr_url || !props.config.callback_url) return ''
  const params = new URLSearchParams({
    agentid: props.config.agent_id ?? '',
    appid: props.config.corp_id ?? '',
    lang: localStorage.getItem('MaxKB-locale') === 'en-US' ? 'en' : 'zh',
    login_type: 'CorpApp',
    panel_size: 'small',
    redirect_uri: props.config.callback_url,
    state: 'fit2cloud-wecom-qr',
  })
  return `${props.config.qr_url}?${params}`
})
</script>

<template>
  <iframe
    v-if="iframeUrl"
    :src="iframeUrl"
    class="-mt-8 h-95 w-full border-0"
    title="企业微信扫码登录"
  />
</template>
