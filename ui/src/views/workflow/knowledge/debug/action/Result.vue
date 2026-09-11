<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import type { KnowledgeWorkflowAction } from '@/api/types'
import ExecutionDetailContent from '@/workflow-canvas/details/index.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'DebugResult' })

const props = defineProps<{ knowledgeId: string; actionId: string }>()

const TERMINAL_STATES = ['SUCCESS', 'FAILURE', 'REVOKE', 'REVOKED']
const POLL_INTERVAL = 2000

const knowledgeAction = ref<KnowledgeWorkflowAction>()
const state = computed(() => knowledgeAction.value?.state ?? 'PENDING')
const detail = computed<ExecutionNodeDetail[]>(() => (knowledgeAction.value ? (Object.values(knowledgeAction.value.details) as ExecutionNodeDetail[]) : []))

let pollingTimer: ReturnType<typeof setTimeout> | null = null

function stopPolling() {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
}

function pollAction() {
  KnowledgeWorkflowApi.getKnowledgeWorkflowAction(props.knowledgeId, props.actionId)
    .then((action) => {
      knowledgeAction.value = action
    })
    .finally(() => {
      if (TERMINAL_STATES.includes(state.value)) {
        stopPolling()
      } else {
        pollingTimer = setTimeout(pollAction, POLL_INTERVAL)
      }
    })
}

function startPolling() {
  stopPolling()
  knowledgeAction.value = undefined
  pollingTimer = setTimeout(pollAction, 0)
}

watch(() => props.actionId, startPolling, { immediate: true })

onUnmounted(stopPolling)
</script>

<template>
  <div>
    <h4 class="mb-4 mt-1">执行详情</h4>
    <div class="mb-4">
      <el-alert v-if="state === 'SUCCESS'" title="执行成功" type="success" show-icon :closable="false" />
      <el-alert v-else-if="state === 'FAILURE'" title="执行失败" type="error" show-icon :closable="false" />
      <el-alert v-else-if="state === 'REVOKE' || state === 'REVOKED'" title="已取消" type="warning" show-icon :closable="false" />
      <el-alert v-else title="执行中" type="info" show-icon :closable="false" />
    </div>
    <ExecutionDetailContent :detail="detail" :workflow-mode="WorkflowMode.Knowledge" />
  </div>
</template>
