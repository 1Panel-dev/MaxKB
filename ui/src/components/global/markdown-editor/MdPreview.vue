<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview as MdPreviewV3 } from 'md-editor-v3'
import { useI18n } from 'vue-i18n'
import { MARKDOWN_LOCALES, normalizeLocale } from '@/locales/config'
import { sanitizeMarkdown } from './sanitize'

defineOptions({ name: 'MdPreview', inheritAttrs: false })

const { locale } = useI18n({ useScope: 'global' })
const language = computed(() => MARKDOWN_LOCALES[normalizeLocale(locale.value)])
</script>

<template>
  <MdPreviewV3 class="mk-markdown-editor" :language="language" :code-foldable="false" v-bind="$attrs" :sanitize="sanitizeMarkdown" />
</template>

<style scoped lang="scss"></style>
