<script setup lang="ts">
import { nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/stores'
import type { QrCodeConfig } from '@/api/types'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '@/utils/script-loader'

defineOptions({ name: 'DingTalkQrCode' })

const props = defineProps<{ config: QrCodeConfig }>()
const router = useRouter()
const { auth } = useStore()

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
      await auth.asyncLoginWithDingTalk(authCode)
      await router.push({ name: 'workspace-home', params: { workspaceId: 'default' } })
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
  <div class="mt-6 flex-center">
    <img src="@/assets/logo/logo_dingtalk.svg" alt="" width="24px" class="mr-2" />
    <h2>钉钉扫码登录</h2>
  </div>
  <div class="ding-talk-layout">
    <div id="dingtalk-qr-code" />
  </div>
</template>
<style lang="scss" scoped>
.ding-talk-layout {
  margin: auto;
  width: 280px;
  height: 280px;
}
</style>
