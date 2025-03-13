<template>
  <div class="flex-center mb-16">
    <img src="@/assets/logo_dingtalk.svg" alt="" width="24px" class="mr-4" />
    <h2>{{ $t('views.system.authentication.scanTheQRCode.dingtalkQrCode') }}</h2>
  </div>
  <div class="ding-talk-qrName">
    <div id="ding-talk-qr"></div>
  </div>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { useScriptTag } from '@vueuse/core'
import { ref, watch } from 'vue'
import useStore from '@/stores'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'

// 声明 DTFrameLogin 和 QRLogin 的类型
declare global {
  interface Window {
    DTFrameLogin: (
      frameParams: IDTLoginFrameParams,
      loginParams: IDTLoginLoginParams,
      successCbk: (result: IDTLoginSuccess) => void,
      errorCbk?: (errorMsg: string) => void
    ) => void
    QRLogin: (QRLogin: qrLogin) => Record<any, any>
  }
}

// 定义接口类型
interface IDTLoginFrameParams {
  id: string
  width?: number
  height?: number
}

interface IDTLoginLoginParams {
  redirect_uri: string
  response_type: string
  client_id: string
  scope: string
  prompt: string
  state?: string
  org_type?: string
  corpId?: string
  exclusiveLogin?: string
  exclusiveCorpId?: string
}

interface IDTLoginSuccess {
  redirectUrl: string
  authCode: string
  state?: string
}

interface qrLogin {
  id: string
  goto: string
  width: string
  height: string
  style?: string
}

const props = defineProps<{
  config: {
    app_secret: string
    app_key: string
    corp_id: string
  }
}>()

const router = useRouter()
const { user } = useStore()
const { load } = useScriptTag('https://g.alicdn.com/dingding/h5-dingtalk-login/0.21.0/ddlogin.js')
const isConfigReady = ref(false)

const initActive = async () => {
  try {
    await load(true)
    if (!isConfigReady.value) {
      return
    }

    const data = {
      appKey: props.config.app_key,
      appSecret: props.config.app_secret,
      corp_id: props.config.corp_id
    }

    const redirectUri = encodeURIComponent(window.location.origin)
    window.DTFrameLogin(
      {
        id: 'ding-talk-qr',
        width: 280,
        height: 280
      },
      {
        redirect_uri: redirectUri,
        client_id: data.appKey,
        scope: 'openid corpid',
        response_type: 'code',
        state: 'fit2cloud-ding-qr',
        prompt: 'consent',
        corpId: data.corp_id
      },
      (loginResult) => {
        const authCode = loginResult.authCode
        user.dingCallback(authCode).then(() => {
          router.push({ name: 'home' })
        })
      },
      (errorMsg: string) => {
        MsgError(errorMsg)
      }
    )
  } catch (error) {
    console.error(error)
  }
}

watch(
  () => props.config,
  (newConfig) => {
    if (newConfig.app_key && newConfig.corp_id) {
      isConfigReady.value = true
      initActive()
    }
  },
  { immediate: true }
)
</script>

<style lang="scss">
.ding-talk-qrName {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  height: 280px;
  width: 280px;
  margin: 0 auto;
}
</style>
