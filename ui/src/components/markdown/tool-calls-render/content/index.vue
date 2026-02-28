<template>
  <component :is="kw[content.type]" :content="content"></component>
</template>
<script setup lang="ts">
import SimpleToolCalls from './simple-tool-calls/index.vue'
import { type ToolCalls } from '@/components/markdown/tool-calls-render/index'
defineProps<{
  content: ToolCalls
}>()
const kw: any = {
  'simple-tool-calls': SimpleToolCalls,
}
</script>
<style lang="scss" scoped></style>
