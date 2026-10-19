<template>
  <component v-if="typeRenderers[content.type]" :is="typeRenderers[content.type]" :content="content" />
  <TextItem v-else :content="content" />
</template>

<script setup lang="ts">
import TextItem from './items/text.vue'
import HtmlItem from './items/html.vue'
import ReasoningItem from './items/reasoning.vue'
import ToolItem from './items/tool/index.vue'
import GroupToolItem from './items/group-tool/index.vue'
import GroupItem from './items/group/index.vue'
import FormItem from './items/form.vue'
import FailureItem from './items/failure.vue'
import QuestionItem from './items/question.vue'

const typeRenderers: Record<string, any> = {
  TEXT: TextItem,
  HTML: HtmlItem,
  REASONING: ReasoningItem,
  TOOL: ToolItem,
  GROUP_TOOL: GroupToolItem,
  GROUP: GroupItem,
  FORM: FormItem,
  FAILURE: FailureItem,
  QUESTION: QuestionItem,
}

defineProps<{ content: any }>()
</script>
