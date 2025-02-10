<template>
  <div id="wecom-qr" class="wecom-qr" style="margin-left: 50px"></div>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import * as ww from '@wecom/jssdk'
import {
  WWLoginLangType,
  WWLoginPanelSizeType,
  WWLoginRedirectType,
  WWLoginType
} from '@wecom/jssdk'
import { ref, nextTick, defineProps } from 'vue'
import { MsgError } from '@/utils/message'
import useStore from '@/stores'
import { getBrowserLang } from '@/locales/index'
const router = useRouter()

const wwLogin = ref({})
const obj = ref<any>({ isWeComLogin: false })
const { user } = useStore()

const props = defineProps<{
  config: {
    app_secret: string
    app_key: string
    corp_id?: string
    agent_id?: string
  }
}>()

const init = async () => {
  await nextTick() // 确保DOM已更新
  const data = {
    corpId: props.config.corp_id,
    agentId: props.config.agent_id
  }
  const lang = localStorage.getItem('MaxKB-locale') || getBrowserLang() || 'en-US'
  const redirectUri = window.location.origin
  try {
    wwLogin.value = ww.createWWLoginPanel({
      el: '#wecom-qr',
      params: {
        login_type: WWLoginType.corpApp,
        appid: data.corpId || '',
        agentid: data.agentId,
        redirect_uri: redirectUri,
        state: 'fit2cloud-wecom-qr',
        lang: lang === 'zh-CN' || lang === 'zh-Hant' ? WWLoginLangType.zh : WWLoginLangType.en,
        redirect_type: WWLoginRedirectType.callback,
        panel_size: WWLoginPanelSizeType.small
      },
      onCheckWeComLogin: obj.value,
      async onLoginSuccess({ code }: any) {
        user.wecomCallback(code).then(() => {
          setTimeout(() => {
            router.push({ name: 'home' })
          })
        })
      },
      onLoginFail(err) {
        MsgError(`${err.errMsg}`)
      }
    })
  } catch (error) {
    console.error('Error initializing login panel:', error)
  }
}

init()
</script>

<style scoped lang="scss">
.wecom-qr {
  margin-top: -20px;
  height: 331px;
}
</style>
