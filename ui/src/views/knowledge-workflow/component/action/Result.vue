<template>
  <div>
    <h4 class="title-decoration-1 mb-16 mt-4">
      {{ $t('chat.executionDetails.title') }}
    </h4>
    <div class="mb-16" v-if="!isRecord">
      <!-- 执行结果 -->
      <el-alert
        v-if="state == 'SUCCESS'"
        :title="$t('common.status.success')"
        type="success"
        show-icon
        :closable="false"
      />
      <el-alert
        v-if="state == 'FAILURE'"
        :title="$t('common.status.fail')"
        type="error"
        show-icon
        :closable="false"
      />
    </div>
    <ExecutionDetailContent :detail="detail" app-type="WORK_FLOW"></ExecutionDetailContent>
  </div>
</template>
<script setup lang="ts">
import { onUnmounted, ref, computed, watch } from 'vue'

import ExecutionDetailContent from '@/components/ai-chat/component/knowledge-source-component/ExecutionDetailContent.vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
const route = useRoute()
const props = defineProps<{ id: string; knowledge_id: string; isRecord: boolean }>()
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
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const knowledge_action = ref<any>()
let pollingTimer: any = null

const getKnowledgeWorkflowAction = () => {
  if (pollingTimer == null) {
    return
  }
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getWorkflowAction(props.knowledge_id, props.id)
    .then((ok: any) => {
      knowledge_action.value = ok.data
    })
    .finally(() => {
      if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(state.value)) {
        stopPolling()
      } else {
        // 请求完成后再设置下次轮询
        pollingTimer = setTimeout(getKnowledgeWorkflowAction, 2000)
      }
    })
}

const stopPolling = () => {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
}

// 启动轮询
pollingTimer = setTimeout(getKnowledgeWorkflowAction, 0)

watch(
  () => props.id,
  () => {
    stopPolling()
    pollingTimer = setTimeout(getKnowledgeWorkflowAction, 0)
  },
)

onUnmounted(() => {
  stopPolling()
})
</script>
<style lang="scss"></style>
