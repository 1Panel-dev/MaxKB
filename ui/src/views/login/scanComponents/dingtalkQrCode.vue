<script setup lang="ts">
import { nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { QrCodeConfig } from '@/api/admin/auth/types'
import { useStore } from '@/stores'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '../../../utils/script-loader'

defineOptions({ name: 'DingTalkQrCode' })

const props = defineProps<{ config: QrCodeConfig }>()
const router = useRouter()
const { login } = useStore()

const initialize = async () => {
  if (!props.config.app_key || !props.config.corp_id) return
  await loadLoginScript(
    'https://g.alicdn.com/dingding/h5-dingtalk-login/0.21.0/ddlogin.js',
    'dingtalk-login-sdk',
  )
  await nextTick()
  if (!window.DTFrameLogin) throw new Error('钉钉扫码 SDK 加载失败')
  window.DTFrameLogin(
    { id: 'dingtalk-qr-code', width: 280, height: 280 },
    {
      client_id: props.config.app_key,
      corpId: props.config.corp_id,
      prompt: 'consent',
      redirect_uri: window.location.origin,
      response_type: 'code',
      scope: 'openid corpid',
      state: 'fit2cloud-ding-qr',
    },
    async ({ authCode }) => {
      await login.asyncLoginWithDingTalk(authCode)
      await router.push({ name: 'workspace-home' })
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
  <div class="mb-4 text-center">
    <h2>钉钉扫码登录</h2>
  </div>
  <div id="dingtalk-qr-code" class="mx-auto size-70 rounded-lg border border-N200" />
</template>
