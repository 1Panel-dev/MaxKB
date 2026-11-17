<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeWorkflowAction, KnowledgeWorkflowApi } from '@/api/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'DebugResult' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api?: KnowledgeWorkflowApi; knowledgeId: string; actionId: string }>()

const TERMINAL_STATES = ['SUCCESS', 'FAILURE', 'REVOKE', 'REVOKED']
const POLL_INTERVAL = 2000

const knowledgeAction = ref<KnowledgeWorkflowAction>()
const state = computed(() => knowledgeAction.value?.state ?? 'PENDING')
const detail = computed<ExecutionNodeDetail[]>(() =>
  knowledgeAction.value ? (Object.values(knowledgeAction.value.details) as ExecutionNodeDetail[]) : [],
)

let pollingTimer: ReturnType<typeof setTimeout> | null = null

function stopPolling() {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
}

function pollAction() {
  ;(props.api ?? WorkflowApi)
    .getKnowledgeWorkflowAction(props.knowledgeId, props.actionId)
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

onMounted(startPolling)

onUnmounted(stopPolling)
</script>

<template>
  <div>
    <h4 class="mb-4 mk-title-decoration">{{ t('workflow.executionResult.title') }}</h4>
    <!-- // TODO 这里状态ui没有考虑执行中情况 -->
    <div class="mb-4">
      <el-alert v-if="state === 'SUCCESS'" :title="t('workflow.executionResult.success')" type="success" show-icon :closable="false" />
      <el-alert v-else-if="state === 'FAILURE'" :title="t('workflow.executionResult.failure')" type="error" show-icon :closable="false" />
      <el-alert
        v-else-if="state === 'REVOKE' || state === 'REVOKED'"
        :title="t('workflow.executionResult.canceled')"
        type="warning"
        show-icon
        :closable="false"
      />
      <el-alert v-else :title="t('workflow.executionResult.running')" type="info" show-icon :closable="false" />
    </div>
    <ExecutionDetailContent :detail="detail" :workflow-mode="WorkflowMode.Knowledge" />
  </div>
</template>
