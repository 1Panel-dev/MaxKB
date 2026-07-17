<template>
  <component v-if="typeRenderers[content.type]" :is="typeRenderers[content.type]" :content="content" v-bind="$attrs" />
  <TextItem v-else :content="content" v-bind="$attrs" />
</template>

<script setup lang="ts">
import TextItem from './text.vue'
import ReasoningItem from './reasoning.vue'
import ToolItem from './tool.vue'
import FormItem from './form.vue'
import FailureItem from './failure.vue'

const typeRenderers: Record<string, any> = {
  TEXT: TextItem,
  REASONING: ReasoningItem,
  TOOL: ToolItem,
  FORM: FormItem,
  FAILURE: FailureItem,
}

defineProps<{ content: any }>()
</script>
