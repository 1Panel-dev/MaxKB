<script setup lang="ts">
import { computed } from 'vue'
import { MdEditor as MdEditorV3 } from 'md-editor-v3'
import { useI18n } from 'vue-i18n'
import { sanitizeMarkdown } from './sanitize'
import { getMarkdownLocale } from '@/locales/config'

defineOptions({ name: 'MdEditor', inheritAttrs: false })

defineSlots<{
  defFooters?(): unknown
}>()

const { locale } = useI18n({ useScope: 'global' })
const language = computed(() => getMarkdownLocale(locale.value))
</script>

<template>
  <MdEditorV3 class="mk-markdown-editor" :language="language" no-prettier v-bind="$attrs" :sanitize="sanitizeMarkdown">
    <template #defFooters>
      <slot name="defFooters" />
    </template>
  </MdEditorV3>
</template>
