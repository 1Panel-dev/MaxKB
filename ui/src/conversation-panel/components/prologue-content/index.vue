<script setup lang="ts">
import type { ConversationAppInfo } from '../../core/types'
import ContentList from '../content-list/index.vue'

defineOptions({ name: 'ConversationPrologueContent' })

defineProps<{
  /** 已格式化的开场白，见 formatPrologue。 */
  prologue: string
  appInfo: ConversationAppInfo | null
}>()
</script>

<template>
  <ContentList :content-list="[{ type: 'TEXT', id: 'prologue', content: prologue }]" />
</template>
