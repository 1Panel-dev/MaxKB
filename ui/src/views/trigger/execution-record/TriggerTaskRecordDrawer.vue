<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, TriggerTaskRecord } from '@/api/types'
import { RESOURCE_TYPE, STATE_TYPES } from '@/api/enums'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { EXECUTION_STATUS_OPTIONS } from '@/constants/state'
import { toOrderBy } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'

const { t } = useI18n({ useScope: 'global' })

/* 当前触发器记录查询 */
const visible = ref(false)
const triggerId = ref('')
const loading = ref(false)
const recordData = ref<TriggerTaskRecord[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const orderBy = ref<string>()
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.status.label'),
    value: 'state',
    options: [
      { label: t(EXECUTION_STATUS_OPTIONS[STATE_TYPES.SUCCESS].labelKey), value: STATE_TYPES.SUCCESS },
      { label: t(EXECUTION_STATUS_OPTIONS[STATE_TYPES.STARTED].labelKey), value: STATE_TYPES.STARTED },
      { label: t(EXECUTION_STATUS_OPTIONS[STATE_TYPES.FAILURE].labelKey), value: STATE_TYPES.FAILURE },
    ],
  },
  {
    label: t('resource.executionRecords.resourceType'),
    value: 'source_type',
    options: [
      { label: t('application.title'), value: RESOURCE_TYPE.APPLICATION },
      { label: t('tool.title'), value: RESOURCE_TYPE.TOOL },
    ],
  },
])
function loadRecords(page = pagination.value.currentPage): Promise<TriggerTaskRecord[]> {
  loading.value = true
  return TriggerApi.getTriggerTaskRecordPage(
    triggerId.value,
    { currentPage: page, pageSize: pagination.value.pageSize },
    { ...searchQuery.value, order: orderBy.value },
  )
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
  searchQuery.value = query ?? {}
  pagination.value.currentPage = 1
  loadRecords()
}

/* 执行时间排序：接口字段使用 ett 表别名，切换排序后回到第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort, (prop) => `ett.${prop}`)
  pagination.value.currentPage = 1
  return loadRecords()
}

function open(id: string) {
  triggerId.value = id
  orderBy.value = undefined
  recordData.value = []
  pagination.value = { currentPage: 1, pageSize: 20, total: 0 }
  visible.value = true
  loadRecords()
}

/* 详情与跨页浏览 */
const detailVisible = ref(false)
const currentRecord = ref<TriggerTaskRecord>()
const recordIndex = computed(() => recordData.value.findIndex((record) => record.id === currentRecord.value?.id))
const previousDisabled = computed(() => loading.value || recordIndex.value < 0 || (recordIndex.value === 0 && pagination.value.currentPage === 1))
const nextDisabled = computed(
  () =>
    loading.value ||
    recordIndex.value < 0 ||
    (pagination.value.currentPage - 1) * pagination.value.pageSize + recordIndex.value + 1 >= pagination.value.total,
)
function showDetails(record: TriggerTaskRecord) {
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
  <MkDrawer v-model="visible" :title="t('resource.executionRecords.title')" size="840" @close="closeDetails">
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
      @sort-change="handleSortChange"
    >
      <el-table-column :label="t('trigger.executionRecords.task')" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex-align-center gap-2">
            <ApplicationIcon v-if="row.source_type === RESOURCE_TYPE.APPLICATION" :icon="row.source_icon" :size="20" />
            <ToolIcon v-else :icon="row.source_icon" :type="row.type" :size="20" />
            <span class="min-w-0 flex-1 truncate">{{ row.source_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.type')" width="80">
        <template #default="{ row }">{{ row.source_type === RESOURCE_TYPE.APPLICATION ? t('application.title') : t('tool.title') }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status.label')" width="100">
        <template #default="{ row }: { row: TriggerTaskRecord }">
          <MkStatusLabel
            v-if="EXECUTION_STATUS_OPTIONS[row.state]"
            :type="EXECUTION_STATUS_OPTIONS[row.state].type"
            :label="t(EXECUTION_STATUS_OPTIONS[row.state].labelKey)"
            :icon="EXECUTION_STATUS_OPTIONS[row.state].icon"
          />
          <span v-else>{{ row.state }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.duration')" width="90">
        <template #default="{ row }">{{ row.run_time == null ? '-' : `${row.run_time.toFixed(2)} s` }}</template>
      </el-table-column>
      <el-table-column :label="t('resource.executionRecords.executionTime')" prop="create_time" width="180" sortable>
        <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" width="70">
        <template #default="{ row }">
          <!-- 查看执行详情 -->
          <MkTooltip :content="t('resource.executionRecords.detailTitle')" placement="top">
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
    :previous-disabled="previousDisabled"
    :next-disabled="nextDisabled"
    @previous="moveRecord(-1)"
    @next="moveRecord(1)"
  />
</template>
