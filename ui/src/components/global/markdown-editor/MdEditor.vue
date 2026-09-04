<script setup lang="ts">
import { computed } from 'vue'
import { MdEditor as MdEditorV3 } from 'md-editor-v3'
import { useStore } from '@/stores'

defineOptions({ name: 'MdEditor', inheritAttrs: false })

defineSlots<{
  defFooters?(): unknown
}>()

const { user } = useStore()
const language = computed(() => {
  const currentLanguage = user.language.toLowerCase()
  if (['zh-tw', 'zh-hant', 'zh-hk', 'zh-mo'].includes(currentLanguage)) return 'zh-TW'
  return currentLanguage.startsWith('zh') ? 'zh-CN' : 'en-US'
})
</script>

<template>
  <MdEditorV3 class="mk-markdown-editor" :language="language" no-prettier v-bind="$attrs">
    <template #defFooters>
      <slot name="defFooters" />
    </template>
  </MdEditorV3>
</template>
