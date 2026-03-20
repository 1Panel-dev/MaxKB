<template>
  <div>
    <p class="mt-8 mb-8">{{ $t('common.param.inputParam') }}：</p>
    <span class="color-secondary">{{ content.content.input }}</span>
    <p class="mt-8 mb-8">{{ $t('common.param.outputParam') }}：</p>
    <span class="color-secondary"><pre>{{ content.content.output }}</pre></span>
  </div>
</template>
<script setup lang="ts">
import { type ToolCalls } from '@/components/markdown/tool-calls-render/index'
defineProps<{
  content: ToolCalls
}>()
</script>
<style lang="scss" scoped></style>
