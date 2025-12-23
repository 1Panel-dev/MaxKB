<template>
  <MdPreview
    :language="language"
    noIconfont
    noPrettier
    :sanitize="sanitize"
    :codeFoldable="false"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview, config } from 'md-editor-v3'
import { getBrowserLang } from '@/locales/index'
import useStore from '@/stores'
// 引入公共库中的语言配置
import ZH_TW from '@vavt/cm-extension/dist/locale/zh-TW'
import sanitizeHtml from 'sanitize-html'
defineOptions({ name: 'MdPreview' })

const emit = defineEmits(['clickPreview'])

const { user } = useStore()
const language = computed(() => user.getLanguage() || getBrowserLang() || '')
config({
  editorConfig: {
    languageUserDefined: {
      'zh-Hant': ZH_TW,
    },
  },
})
const sanitize = (html: any) => {
  return sanitizeHtml(html)
}
</script>

<style lang="scss" scoped>
:deep(audio) {
  width: 300px;
  height: 43px;
}
</style>
