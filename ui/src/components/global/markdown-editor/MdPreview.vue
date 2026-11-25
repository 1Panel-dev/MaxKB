<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview as MdPreviewV3 } from 'md-editor-v3'
import { useI18n } from 'vue-i18n'
import { sanitizeMarkdown } from './sanitize'
import { getMarkdownLocale } from '@/locales/config'

defineOptions({ name: 'MdPreview', inheritAttrs: false })

const { locale } = useI18n({ useScope: 'global' })
const language = computed(() => getMarkdownLocale(locale.value))
</script>

<template>
  <MdPreviewV3 class="mk-markdown-editor" :language="language" :code-foldable="false" v-bind="$attrs" :sanitize="sanitizeMarkdown" />
</template>

<style scoped lang="scss"></style>
