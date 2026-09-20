<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import type WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import { STATE_TYPES } from '@/api/enums'
import type { Dict, KnowledgeExecutionRecord } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { MsgConfirm } from '@/utils/message'
import { STATE_LABELS } from '@/constants/state'

const props = defineProps<{ api: typeof WorkflowApi; knowledgeId: string }>()
const emit = defineEmits<{ closed: [] }>()

/* 知识库执行记录查询 */
const visible = ref(false)
const loading = ref(false)
const recordData = ref<KnowledgeExecutionRecord[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const searchFields = [
  { label: '发起人', value: 'user_name' },
  {
    label: '状态',
    value: 'state',
    options: [STATE_TYPES.PENDING, STATE_TYPES.STARTED, STATE_TYPES.SUCCESS, STATE_TYPES.FAILURE, STATE_TYPES.REVOKE, STATE_TYPES.REVOKED].map(
      (state) => ({
        label: STATE_LABELS[state],
        value: state,
      }),
    ),
  },
]
let pollingTimer: ReturnType<typeof setTimeout> | undefined
function stopPolling() {
  clearTimeout(pollingTimer)
  pollingTimer = undefined
}
function schedulePolling() {
  stopPolling()
  if (visible.value)
    pollingTimer = setTimeout(() => {
      void loadRecords(pagination.value.currentPage, false).catch(() => {})
    }, 6000)
}
function loadRecords(page = pagination.value.currentPage, showLoading = true): Promise<KnowledgeExecutionRecord[]> {
  stopPolling()
  if (showLoading) loading.value = true
  return props.api
    .getKnowledgeExecutionRecordPage(props.knowledgeId, { currentPage: page, pageSize: pagination.value.pageSize }, searchQuery.value)
    .then((result) => {
      recordData.value = result.records
      if (currentRecord.value) currentRecord.value = result.records.find((record) => record.id === currentRecord.value?.id) ?? currentRecord.value
      pagination.value = { currentPage: result.current, pageSize: result.size, total: result.total }
      return result.records
    })
    .finally(() => {
      if (showLoading) loading.value = false
      schedulePolling()
    })
}

function searchRecords(query?: Dict<unknown>) {
  closeDetails()
  searchQuery.value = query ?? {}
  pagination.value.currentPage = 1
  loadRecords()
}

function open() {
  searchQuery.value = undefined
  closeDetails()
  recordData.value = []
  pagination.value = { currentPage: 1, pageSize: 20, total: 0 }
  visible.value = true
  loadRecords()
}

/* 详情与跨页浏览 */
const detailVisible = ref(false)
const currentRecord = ref<KnowledgeExecutionRecord>()
const recordIndex = computed(() => recordData.value.findIndex((record) => record.id === currentRecord.value?.id))
const previousDisabled = computed(() => loading.value || recordIndex.value < 0 || (recordIndex.value === 0 && pagination.value.currentPage === 1))
const nextDisabled = computed(
  () =>
    loading.value ||
    recordIndex.value < 0 ||
    (pagination.value.currentPage - 1) * pagination.value.pageSize + recordIndex.value + 1 >= pagination.value.total,
)
function showDetails(record: KnowledgeExecutionRecord) {
  currentRecord.value = record
  detailVisible.value = true
}
function moveRecord(direction: -1 | 1) {
  if (direction === -1 ? previousDisabled.value : nextDisabled.value) return
  const nextIndex = recordIndex.value + direction
  const record = recordData.value[nextIndex]
  if (record) {
    currentRecord.value = record
    return
  }
  return loadRecords(pagination.value.currentPage + direction)
    .then((pageRecords) => {
      const target = direction === 1 ? pageRecords[0] : pageRecords.at(-1)
      if (target) currentRecord.value = target
      else detailVisible.value = false
    })
    .catch(() => {})
}
function closeDetails() {
  detailVisible.value = false
  currentRecord.value = undefined
}
/* 取消执行后刷新记录，关闭或卸载时停止轮询。 */
const cancelling = ref(false)
function cancelExecution(record: KnowledgeExecutionRecord) {
  return MsgConfirm('提示', '确认取消当前执行任务？', { confirmButtonText: '确认' })
    .then(() => {
      cancelling.value = true
      return props.api.postCancelKnowledgeWorkflowAction(props.knowledgeId, record.id).then(() => loadRecords())
    })
    .catch(() => {})
    .finally(() => {
      cancelling.value = false
    })
}
function close() {
  visible.value = false
  stopPolling()
  closeDetails()
}
onBeforeUnmount(() => {
  visible.value = false
  stopPolling()
})
defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" title="执行记录" size="840" @close="close" @closed="emit('closed')">
    <div class="mb-4">
      <MkComplexSearch v-if="visible" :fields="searchFields" class="w-76!" @change="searchRecords" />
    </div>
    <MkTable
      v-if="visible"
      v-loading="loading"
      :data="recordData"
      v-model:pagination-config="pagination"
      :max-table-height="230"
      @current-change="loadRecords()"
      @size-change="loadRecords()"
    >
      <el-table-column label="发起人" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">{{ row.meta?.user_name || '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100"
        ><template #default="{ row }"><MkStatusLabel :status="row.state" /></template
      ></el-table-column>
      <el-table-column label="耗时" width="90"
        ><template #default="{ row }">{{ row.run_time == null ? '-' : `${row.run_time.toFixed(2)} s` }}</template></el-table-column
      >
      <el-table-column label="执行时间" prop="create_time" width="180"
        ><template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template></el-table-column
      >
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <!-- 查看执行详情 -->
          <MkTooltip content="执行详情" placement="top">
            <el-button text type="primary" @click="showDetails(row)"><MkIcon name="icon_describe_outlined" /></el-button>
          </MkTooltip>
          <!-- 取消执行 -->
          <MkTooltip v-if="row.state === STATE_TYPES.PENDING || row.state === STATE_TYPES.STARTED" content="取消执行" placement="top">
            <el-button text type="danger" :disabled="cancelling || loading" @click="cancelExecution(row)"
              ><MkIcon name="icon_close_outlined"
            /></el-button>
          </MkTooltip>
        </template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
  <ExecutionDetailDrawer
    v-if="currentRecord"
    v-model="detailVisible"
    :record="currentRecord"
    :api="api"
    :knowledge-id="knowledgeId"
    :previous-disabled="previousDisabled"
    :next-disabled="nextDisabled"
    @previous="moveRecord(-1)"
    @next="moveRecord(1)"
  />
</template>
