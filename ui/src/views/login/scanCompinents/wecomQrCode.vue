<template>
  <iframe :src="iframeUrl" width="100%" height="380px" frameborder="0"
          style="margin-top: -30px"></iframe>
</template>

<script lang="ts" setup>
import {ref, nextTick, defineProps} from 'vue'
import {getBrowserLang} from '@/locales'

const props = defineProps<{
  config: {
    app_secret: string
    app_key: string
    corp_id?: string
    agent_id?: string
    callback_url: string
  }
}>()

const iframeUrl = ref('')
const init = async () => {
  await nextTick() // 确保DOM已更新
  const data = {
    corpId: props.config.corp_id,
    agentId: props.config.agent_id,
    redirectUri: props.config.callback_url,
  }
  let lang = localStorage.getItem('MaxKB-locale') || getBrowserLang() || 'en-US'
  if (lang === 'en-US') {
    lang = 'en'
  } else {
    lang = 'zh'
  }
  const redirectUri = encodeURIComponent(data.redirectUri)
  console.log('redirectUri', data.redirectUri)
  // 手动构建生成二维码的url
  iframeUrl.value = `https://login.work.weixin.qq.com/wwlogin/sso/login?login_type=CorpApp&appid=${data.corpId}&agentid=${data.agentId}&redirect_uri=${redirectUri}&state=fit2cloud-wecom-qr&lang=${lang}&panel_size=small`
}

init()
</script>

<style scoped lang="scss">
#wecom-qr {
  margin-top: -20px;
  height: 331px;
  justify-content: center;

}
</style>
