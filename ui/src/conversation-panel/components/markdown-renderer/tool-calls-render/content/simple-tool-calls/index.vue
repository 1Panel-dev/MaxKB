<template>
  <div>
    <p class="my-2">输入参数：</p>
    <span class="text-N500">{{ content.content.input }}</span>
    <p class="my-2">输出参数：</p>
    <span class="text-N500">
      <pre>{{ content.content.output }}</pre>
    </span>
  </div>
</template>
<script setup lang="ts">
import { type ToolCalls } from '../../index'
defineProps<{
  content: ToolCalls
}>()
</script>
<style lang="scss" scoped></style>
