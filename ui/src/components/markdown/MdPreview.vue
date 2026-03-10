<template>
  <MdPreview
    :language="language"
    noIconfont
    noPrettier
    :codeFoldable="false"
    v-bind="previewAttrs"
  />
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import { MdPreview, config } from 'md-editor-v3'
import { getBrowserLang } from '@/locales/index'
import useStore from '@/stores'
// 引入公共库中的语言配置
import ZH_TW from '@vavt/cm-extension/dist/locale/zh-TW'

defineOptions({ name: 'MdPreview' })
const previewAttrs = useAttrs() as any
const { user } = useStore()
const language = computed(() => user.getLanguage() || getBrowserLang() || '')
config({
  editorConfig: {
    languageUserDefined: {
      'zh-Hant': ZH_TW
    }
  }
})
</script>
