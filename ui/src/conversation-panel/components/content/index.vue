<script setup lang="ts">
import { computed, type Component } from 'vue'
import TextItem from './items/text.vue'
import ReasoningItem from './items/reasoning.vue'
import ToolItem from './items/tool.vue'
import FormItem from './items/form.vue'
import FailureItem from './items/failure.vue'
import QuestionItem from './items/question.vue'

defineOptions({ name: 'ConversationContent' })

const props = defineProps<{
  content: { type: string; [key: string]: unknown }
}>()

const typeRenderers: Partial<Record<string, Component>> = {
  TEXT: TextItem,
  REASONING: ReasoningItem,
  TOOL: ToolItem,
  FORM: FormItem,
  FAILURE: FailureItem,
  QUESTION: QuestionItem,
}

// 未识别的内容类型继续按正文展示。
const contentRenderer = computed(() => typeRenderers[props.content.type] ?? TextItem)
</script>

<template>
  <component :is="contentRenderer" :content="content" />
</template>
