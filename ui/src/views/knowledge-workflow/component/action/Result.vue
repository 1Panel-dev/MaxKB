<template>
  <div>
    <h4 class="title-decoration-1 mb-16 mt-4">
      {{ $t('views.workflow.debug.executionResult') }}
    </h4>
    <div class="mb-16">
      <!-- 执行结果 -->
      <!-- <el-alert
            v-if="isSuccess"
            :title="$t('views.workflow.debug.executionSuccess')"
            type="success"
            show-icon
            :closable="false"
          />
          <el-alert
            v-else
            :title="$t('views.workflow.debug.executionFailed')"
            type="error"
            show-icon
            :closable="false"
          /> -->
    </div>
    <p class="lighter mb-8">{{ $t('chat.executionDetails.title') }}</p>
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
let pollingTimer: any = null

const getKnowledgeWorkflowAction = () => {
  knowledgeApi
    .getWorkflowAction(props.knowledge_id, props.id)
    .then((ok) => {
      knowledge_action.value = ok.data
      if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(state.value)) {
        stopPolling()
      } else {
        // 请求完成后再设置下次轮询
        pollingTimer = setTimeout(getKnowledgeWorkflowAction, 2000)
      }
    })
    .catch(() => {
      // 错误时也继续轮询
      pollingTimer = setTimeout(getKnowledgeWorkflowAction, 2000)
    })
}

const stopPolling = () => {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
}

// 启动轮询
getKnowledgeWorkflowAction()

onUnmounted(() => {
  stopPolling()
})
</script>
<style lang="scss"></style>
