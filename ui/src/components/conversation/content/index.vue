<template>
  <component v-if="typeRenderers[content.type]" :is="typeRenderers[content.type]" :content="content" />
  <TextItem v-else :content="content" />
</template>

<script setup lang="ts">
import TextItem from './items/text.vue'
import ReasoningItem from './items/reasoning.vue'
import ToolItem from './items/tool.vue'
import FormItem from './items/form.vue'
import FailureItem from './items/failure.vue'

const typeRenderers: Record<string, any> = {
  TEXT: TextItem,
  REASONING: ReasoningItem,
  TOOL: ToolItem,
  FORM: FormItem,
  FAILURE: FailureItem
}

defineProps<{ content: any }>()
</script>
