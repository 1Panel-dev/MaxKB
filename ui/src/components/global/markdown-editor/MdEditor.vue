<script setup lang="ts">
import { computed } from 'vue'
import { MdEditor as MdEditorV3 } from 'md-editor-v3'
import { useI18n } from 'vue-i18n'
import { MARKDOWN_LOCALES, normalizeLocale } from '@/locales/config'
import { sanitizeMarkdown } from './sanitize'

defineOptions({ name: 'MdEditor', inheritAttrs: false })

defineSlots<{
  defFooters?(): unknown
}>()

const { locale } = useI18n({ useScope: 'global' })
const language = computed(() => MARKDOWN_LOCALES[normalizeLocale(locale.value)])
</script>

<template>
  <MdEditorV3 class="mk-markdown-editor" :language="language" no-prettier v-bind="$attrs" :sanitize="sanitizeMarkdown">
    <template #defFooters>
      <slot name="defFooters" />
    </template>
  </MdEditorV3>
</template>
