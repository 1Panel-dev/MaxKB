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

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- 内容已经 DOMPurify 净化 -->
  <div class="overflow-x-auto [word-break:break-word]" v-html="sanitizedHtml" />
</template>
