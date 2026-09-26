<script setup lang="ts">
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
import { computed, ref } from 'vue'
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE, STATE_TYPES } from '@/api/enums'
import type { DocumentStatusMeta, DocumentTaskState, DocumentTaskType, State } from '@/api/types'

defineOptions({ name: 'DocumentStatus' })
const props = defineProps<{ status: string; statusMeta?: DocumentStatusMeta | null }>()

const DOCUMENT_TASKS = [
  { type: DOCUMENT_TASK_TYPE.EMBEDDING, label: '向量化', startedStatus: STATE_TYPES.EMBEDDING },
  { type: DOCUMENT_TASK_TYPE.GENERATE_PROBLEM, label: '生成问题', startedStatus: STATE_TYPES.GENERATE },
  { type: DOCUMENT_TASK_TYPE.SYNC, label: '同步', startedStatus: STATE_TYPES.SYNC },
  { type: DOCUMENT_TASK_TYPE.TOKENIZE, label: '分词索引', startedStatus: STATE_TYPES.TOKENIZE },
] as const

const DOCUMENT_STATUS_PRIORITY = [
  DOCUMENT_TASK_STATE.REVOKE,
  DOCUMENT_TASK_STATE.STARTED,
  DOCUMENT_TASK_STATE.PENDING,
  DOCUMENT_TASK_STATE.FAILURE,
  DOCUMENT_TASK_STATE.REVOKED,
  DOCUMENT_TASK_STATE.SUCCESS,
] as const

const DOCUMENT_STATUS_DISPLAY: Partial<Record<DocumentTaskState, State>> = {
  [DOCUMENT_TASK_STATE.PENDING]: STATE_TYPES.PENDING,
  [DOCUMENT_TASK_STATE.REVOKE]: STATE_TYPES.REVOKE,
  // 文件状态沿用 v2：取消完成展示成功，明细完成数仍只统计真正成功的分段。
  [DOCUMENT_TASK_STATE.REVOKED]: STATE_TYPES.SUCCESS,
  [DOCUMENT_TASK_STATE.FAILURE]: STATE_TYPES.FAILURE,
  [DOCUMENT_TASK_STATE.SUCCESS]: STATE_TYPES.SUCCESS,
}

interface DocumentTaskStatus {
  type: DocumentTaskType
  label: string
  state: DocumentTaskState
  displayStatus: State
  completed: number
  total: number
  time: string
  failed: boolean
}

function getTaskState(status: string, type: DocumentTaskType) {
  return status.at(-type) ?? DOCUMENT_TASK_STATE.IGNORED
}

/** 按从右起的任务位置解析状态，并汇总对应分段数量。 */
function getDocumentTaskStatuses(status: string, statusMeta?: DocumentStatusMeta | null): DocumentTaskStatus[] {
  return DOCUMENT_TASKS.flatMap((task) => {
    const state = getTaskState(status, task.type) as DocumentTaskState
    const displayStatus = state === DOCUMENT_TASK_STATE.STARTED ? task.startedStatus : DOCUMENT_STATUS_DISPLAY[state]
    if (!displayStatus) return []

    let completed = 0
    let total = 0
    for (const aggregation of statusMeta?.aggs ?? []) {
      total += aggregation.count
      if (getTaskState(aggregation.status, task.type) === DOCUMENT_TASK_STATE.SUCCESS) completed += aggregation.count
    }
    const timeState = state === DOCUMENT_TASK_STATE.REVOKED ? DOCUMENT_TASK_STATE.REVOKED : DOCUMENT_TASK_STATE.PENDING
    return [
      {
        type: task.type,
        label: task.label,
        state,
        displayStatus,
        completed,
        total,
        time: statusMeta?.state_time?.[task.type]?.[timeState]?.slice(0, 19) ?? '',
        failed: state === DOCUMENT_TASK_STATE.FAILURE || state === DOCUMENT_TASK_STATE.REVOKED,
      },
    ]
  })
}

/** 同一状态优先级取左侧任务，与 v2 的 indexOf 规则一致。 */
function getAggregateDocumentStatus(taskStatuses: DocumentTaskStatus[]) {
  for (const state of DOCUMENT_STATUS_PRIORITY) {
    const task = [...taskStatuses].reverse().find((task) => task.state === state)
    if (task) return task
  }
}

// 文件汇总状态与各任务详情共用解析结果。
const visible = ref(false)
const taskStatuses = computed(() => getDocumentTaskStatuses(props.status, props.statusMeta))
const aggregateStatus = computed(() => getAggregateDocumentStatus(taskStatuses.value))
</script>

<template>
  <el-popover
    v-model:visible="visible"
    placement="bottom-start"
    trigger="hover"
    width="auto"
    :show-after="TOOLTIP_SHOW_DELAY"
    :persistent="false"
    :disabled="!aggregateStatus"
  >
    <template #reference>
      <span class="inline-flex cursor-pointer">
        <MkStatusLabel v-if="aggregateStatus" :status="aggregateStatus.displayStatus" />
        <span v-else>-</span>
      </span>
    </template>
    <div v-if="visible" class="space-y-2 p-3">
      <template v-for="task in taskStatuses" :key="task.type">
        <div class="flex-align-center gap-3 whitespace-nowrap">
          <span>{{ task.label }}:</span>
          <MkStatusLabel :status="task.displayStatus" />
          <span :class="task.failed ? 'text-danger' : ''">完成 {{ task.completed }}/{{ task.total }}</span>
          <span v-if="task.time" class="text-N500">{{ task.time }}</span>
        </div>
      </template>
    </div>
  </el-popover>
</template>
