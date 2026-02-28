<template>
  <el-card>
    {{ content.content.input }}
  </el-card>
  <el-card>
    {{ content.content.output }}
  </el-card>
</template>
<script setup lang="ts">
import { type ToolCalls } from '@/components/markdown/tool-calls-render/index'
defineProps<{
  content: ToolCalls
}>()
</script>
<style lang="scss" scoped></style>
