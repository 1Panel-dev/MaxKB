<template>
  <div id="wecom-qr" class="wecom-qr flex"></div>
</template>

<script lang="ts" setup>
import {nextTick, defineProps, onBeforeUnmount} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {getBrowserLang} from '@/locales'
import useStore from '@/stores'

const props = defineProps<{
  config: {
    app_secret: string
    app_key: string
    corp_id?: string
    agent_id?: string
    callback_url: string
    qr_url: string
  }
}>()

const router = useRouter()
const route = useRoute()
const {chatUser} = useStore()

const {
  params: {accessToken},
} = route as any

let iframe: HTMLIFrameElement | null = null

function createTransparentIFrame(el: string) {
  const container = document.querySelector(el)
  if (!container) return null

  const iframeEl = document.createElement('iframe')
  iframeEl.style.cssText = `
    display: block;
    border: none;
    background: transparent;
  `
  iframeEl.referrerPolicy = 'origin'
  iframeEl.setAttribute('frameborder', '0')
  iframeEl.setAttribute('allowtransparency', 'true')
  iframeEl.setAttribute('allow', 'local-network-access')
  container.appendChild(iframeEl)
  return iframeEl
}

function getLang() {
  const lang = localStorage.getItem('MaxKB-locale') || getBrowserLang()
  return lang === 'en-US' ? 'en' : 'zh'
}

function cleanup() {
  iframe?.remove()
  iframe = null
}

const init = async () => {
  await nextTick()

  iframe = createTransparentIFrame('#wecom-qr')
  if (!iframe) return

  const redirectUri = encodeURIComponent(props.config.callback_url)

  iframe.src =
    `${props.config.qr_url}` +
    `?login_type=CorpApp` +
    `&appid=${props.config.corp_id}` +
    `&agentid=${props.config.agent_id}` +
    `&redirect_uri=${redirectUri}` +
    `&state=${accessToken}` +
    `&lang=${getLang()}` +
    `&panel_size=small` +
    `&redirect_type=self`
  iframe.addEventListener('load', (e) => {
    if (iframe?.contentWindow) {
      iframe.contentWindow.postMessage('getToken', '*')
    }
  })
  window.addEventListener('message', (event) => {
    if (event.data.type === 'token') {
      chatUser.setToken(event.data.value)
      router.push({
        name: 'chat',
        params: {accessToken},
        query: route.query,
      })
    }
  })
}

onBeforeUnmount(cleanup)

init()
</script>

<style scoped lang="scss">
#wecom-qr {
  margin-top: -20px;
  height: 360px;
  justify-content: center;
}
</style>
