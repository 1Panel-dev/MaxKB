<template>
  <component :is="kw[content.type]" :content="content"></component>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import SimpleToolCalls from './simple-tool-calls/index.vue'
import { type ToolCalls } from '../index'
defineProps<{
  content: ToolCalls
}>()
const kw: Record<string, Component> = {
  'simple-tool-calls': SimpleToolCalls,
}
</script>
<style lang="scss" scoped></style>
