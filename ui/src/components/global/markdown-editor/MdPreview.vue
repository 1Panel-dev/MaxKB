<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview as MdPreviewV3 } from 'md-editor-v3'
import { useStore } from '@/stores'

defineOptions({ name: 'MdPreview', inheritAttrs: false })

const { user } = useStore()
const language = computed(() => {
  const currentLanguage = user.language.toLowerCase()
  if (['zh-tw', 'zh-hant', 'zh-hk', 'zh-mo'].includes(currentLanguage)) return 'zh-TW'
  return currentLanguage.startsWith('zh') ? 'zh-CN' : 'en-US'
})
</script>

<template>
  <MdPreviewV3 :language="language" :code-foldable="false" v-bind="$attrs" />
</template>

<style scoped>
:deep(audio) {
  width: 300px;
  height: 43px;
}
</style>
