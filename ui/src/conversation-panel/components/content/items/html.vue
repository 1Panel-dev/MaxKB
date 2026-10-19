<template>
  <!-- eslint-disable-next-line vue/no-v-html -- 内容已经 DOMPurify 净化 -->
  <div class="content-html" v-html="sanitizedHtml" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'

defineOptions({ name: 'ContentHtmlItem' })

const props = defineProps<{
  content: { content?: string }
}>()

// 回复内容可能引用用户输入，渲染前净化，去除脚本与事件属性
const sanitizedHtml = computed(() => DOMPurify.sanitize(props.content.content || ''))
</script>

<style scoped lang="scss">
.content-html {
  overflow-x: auto;
  word-break: break-word;
}
</style>
