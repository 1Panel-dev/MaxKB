<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type WorkflowApi from '@/api/admin/workspace/tool/workflow'
import type { Dict, ToolExecutionRecord } from '@/api/types'
import { KNOWLEDGE_TYPE, STATE_TYPES, TOOL_RECORD_SOURCE } from '@/api/enums'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { EXECUTION_STATUS_OPTIONS } from '@/constants/state'
import { toOrderBy } from '@/utils/common'
import { isSystemSharedResource } from '@/utils/resource-context'
import { datetimeFormat } from '@/utils/time'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: typeof WorkflowApi; toolId: string }>()
const emit = defineEmits<{ closed: [] }>()

/* 当前工具记录查询 */
const visible = ref(false)
const loading = ref(false)
const recordData = ref<ToolExecutionRecord[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchInput = ref<Dict<unknown>>({})
const orderBy = ref<string>()
const sourceLabels = reactive({
  [TOOL_RECORD_SOURCE.APPLICATION]: computed(() => t('application.title')),
  [TOOL_RECORD_SOURCE.KNOWLEDGE]: computed(() => t('knowledge.title')),
  [TOOL_RECORD_SOURCE.TOOL]: computed(() => t('tool.title')),
  [TOOL_RECORD_SOURCE.TRIGGER]: computed(() => t('trigger.title')),
})
const sourceTypeOptions = computed(() => [
  { label: sourceLabels[TOOL_RECORD_SOURCE.APPLICATION], value: TOOL_RECORD_SOURCE.APPLICATION },
  { label: sourceLabels[TOOL_RECORD_SOURCE.KNOWLEDGE], value: TOOL_RECORD_SOURCE.KNOWLEDGE },
  { label: sourceLabels[TOOL_RECORD_SOURCE.TOOL], value: TOOL_RECORD_SOURCE.TOOL },
  { label: sourceLabels[TOOL_RECORD_SOURCE.TRIGGER], value: TOOL_RECORD_SOURCE.TRIGGER },
])
const stateOptions = computed(() => [
  { label: EXECUTION_STATUS_OPTIONS[STATE_TYPES.SUCCESS].label, value: STATE_TYPES.SUCCESS },
  { label: EXECUTION_STATUS_OPTIONS[STATE_TYPES.STARTED].label, value: STATE_TYPES.STARTED },
  { label: EXECUTION_STATUS_OPTIONS[STATE_TYPES.FAILURE].label, value: STATE_TYPES.FAILURE },
])
const searchFields = computed(() => [{ label: t('execution.records.triggerSource'), value: 'source_name' }])
const selectedSourceType = ref<string | null>(null)
const selectedState = ref<string | null>(null)
const searchQuery = computed<Dict<unknown>>(() => ({
  ...searchInput.value,
  order: orderBy.value,
  ...(selectedSourceType.value ? { source_type: selectedSourceType.value } : {}),
  ...(selectedState.value ? { state: selectedState.value } : {}),
}))
function loadRecords(page = pagination.value.currentPage): Promise<ToolExecutionRecord[]> {
  loading.value = true
  return props.api
    .getToolExecutionRecordPage(props.toolId, { currentPage: page, pageSize: pagination.value.pageSize }, searchQuery.value)
    .then((result) => {
      recordData.value = result.records
      pagination.value = { currentPage: result.current, pageSize: result.size, total: result.total }
      return result.records
    })
    .finally(() => {
      loading.value = false
    })
}

function searchRecords(query?: Dict<unknown>) {
  searchInput.value = query ?? {}
  pagination.value.currentPage = 1
  loadRecords()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  loadRecords()
}

/* 执行时间排序与触发器记录保持相同的正负字段协议。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort, (prop) => `ett.${prop}`)
  pagination.value.currentPage = 1
  return loadRecords()
}

function open() {
  orderBy.value = undefined
  searchInput.value = {}
  selectedSourceType.value = null
  selectedState.value = null
  closeDetails()
  recordData.value = []
  pagination.value = { currentPage: 1, pageSize: 20, total: 0 }
  visible.value = true
  loadRecords()
}

/* 详情与跨页浏览 */
const detailVisible = ref(false)
const currentRecord = ref<ToolExecutionRecord>()
const recordIndex = computed(() => recordData.value.findIndex((record) => record.id === currentRecord.value?.id))
const previousDisabled = computed(() => loading.value || recordIndex.value < 0 || (recordIndex.value === 0 && pagination.value.currentPage === 1))
const nextDisabled = computed(
  () =>
    loading.value ||
    recordIndex.value < 0 ||
    (pagination.value.currentPage - 1) * pagination.value.pageSize + recordIndex.value + 1 >= pagination.value.total,
)
function showDetails(record: ToolExecutionRecord) {
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
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="t('execution.records.title')" size="840" @close="closeDetails" @closed="emit('closed')">
    <div class="mb-4">
      <MkComplexSearch v-if="visible" :fields="searchFields" @change="searchRecords" />
    </div>
    <MkTable
      v-if="visible"
      v-loading="loading"
      :data="recordData"
      v-model:pagination-config="pagination"
      :max-table-height="230"
      @current-change="loadRecords()"
      @size-change="loadRecords()"
      @sort-change="handleSortChange"
    >
      <el-table-column :label="t('execution.records.triggerSource')" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex-align-center gap-2">
            <ApplicationIcon v-if="row.source_type === TOOL_RECORD_SOURCE.APPLICATION" :icon="row.source_icon" :size="20" />
            <KnowledgeIcon v-else-if="row.source_type === TOOL_RECORD_SOURCE.KNOWLEDGE" :type="KNOWLEDGE_TYPE.WORKFLOW" :size="20" />
            <ToolIcon v-else-if="row.source_type === TOOL_RECORD_SOURCE.TOOL" :icon="row.source_icon ?? undefined" :size="20" />
            <TriggerIcon v-else-if="row.source_type === TOOL_RECORD_SOURCE.TRIGGER" :type="row.trigger_type ?? undefined" :size="20" />
            <span class="min-w-0 flex-1 truncate" :title="row.source_name || '-'">{{ row.source_name || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column v-if="isSystemSharedResource()" prop="workspace_name" :label="t('workspace.title')" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.workspace_name }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.type')" width="90">
        <template #header>
          <MkTableFilter
            mode="single"
            v-model="selectedSourceType"
            :label="t('common.labels.type')"
            :options="sourceTypeOptions"
            @change="handleFilterChange"
          />
        </template>
        <template #default="{ row }">{{ sourceLabels[row.source_type as keyof typeof sourceLabels] || '-' }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status.label')" width="100">
        <template #header>
          <MkTableFilter
            mode="single"
            v-model="selectedState"
            :label="t('common.status.label')"
            :options="stateOptions"
            @change="handleFilterChange"
          />
        </template>
        <template #default="{ row }: { row: ToolExecutionRecord }">
          <MkStatusLabel
            v-if="EXECUTION_STATUS_OPTIONS[row.state]"
            :type="EXECUTION_STATUS_OPTIONS[row.state].type"
            :label="EXECUTION_STATUS_OPTIONS[row.state].label"
            :icon="EXECUTION_STATUS_OPTIONS[row.state].icon"
          />
          <span v-else>{{ row.state }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.duration')" width="90">
        <template #default="{ row }">{{ row.run_time == null ? '-' : `${row.run_time.toFixed(2)} s` }}</template>
      </el-table-column>
      <el-table-column :label="t('execution.records.executionTime')" prop="create_time" width="180" sortable>
        <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" width="70">
        <template #default="{ row }">
          <!-- 查看执行详情 -->
          <MkTooltip :content="t('execution.details.title')" placement="top">
            <el-button text type="primary" @click="showDetails(row)"><MkIcon name="icon_describe_outlined" /></el-button>
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
    :tool-id="toolId"
    :previous-disabled="previousDisabled"
    :next-disabled="nextDisabled"
    @previous="moveRecord(-1)"
    @next="moveRecord(1)"
  />
</template>
