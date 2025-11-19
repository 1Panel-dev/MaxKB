<template>
  <div>
    <ExecutionDetailContent :detail="detail" app-type="WORK_FLOW"></ExecutionDetailContent>
  </div>
</template>
<script setup lang="ts">
import { onUnmounted, ref, computed } from 'vue'
import knowledgeApi from '@/api/knowledge/knowledge'
const props = defineProps<{ id: string; knowledge_id: string }>()
import ExecutionDetailContent from '@/components/ai-chat/component/knowledge-source-component/ExecutionDetailContent.vue'
const detail = computed(() => {
  if (knowledge_action.value) {
    return Object.values(knowledge_action.value.details)
  }
  return []
})
const state = computed(() => {
  if (knowledge_action.value) {
    return knowledge_action.value.state
  }
  return 'PADDING'
})
const knowledge_action = ref<any>()
const getKnowledgeWorkflowAction = () => {
  knowledgeApi.getWorkflowAction(props.knowledge_id, props.id).then((ok) => {
    knowledge_action.value = ok.data
    if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(state.value)) {
      clearInterval(polling)
    }
  })
}
const polling = setInterval(getKnowledgeWorkflowAction, 2000)

onUnmounted(() => {
  clearInterval(polling)
})
</script>
<style lang="scss"></style>
