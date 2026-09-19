<script setup lang="ts">
import { computed, ref } from 'vue'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { RESOURCE_TYPE, STATE_TYPES } from '@/api/enums'
import type { Dict, TriggerTaskRecord } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { STATE_LABELS } from '@/constants/state'

/* 当前触发器记录查询 */
const visible = ref(false)
const triggerId = ref('')
const loading = ref(false)
const recordData = ref<TriggerTaskRecord[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const searchFields = [
  { label: '名称', value: 'name' },
  {
    label: '状态',
    value: 'state',
    options: [
      { label: STATE_LABELS[STATE_TYPES.SUCCESS], value: STATE_TYPES.SUCCESS },
      { label: STATE_LABELS[STATE_TYPES.STARTED], value: STATE_TYPES.STARTED },
      { label: STATE_LABELS[STATE_TYPES.FAILURE], value: STATE_TYPES.FAILURE },
    ],
  },
  {
    label: '资源类型',
    value: 'source_type',
    options: [
      { label: '智能体', value: RESOURCE_TYPE.APPLICATION },
      { label: '工具', value: RESOURCE_TYPE.TOOL },
    ],
  },
]
function loadRecords(page = pagination.value.currentPage): Promise<TriggerTaskRecord[]> {
  loading.value = true
  return TriggerApi.getTriggerTaskRecordPage(triggerId.value, { currentPage: page, pageSize: pagination.value.pageSize }, searchQuery.value)
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

function open(id: string) {
  triggerId.value = id
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
  <MkDrawer v-model="visible" title="执行记录" size="840" @close="closeDetails">
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
      <el-table-column label="触发任务" min-width="130" show-overflow-tooltip>
        <template #default="{ row }"
          ><div class="flex-align-center gap-2">
            <ApplicationIcon v-if="row.source_type === RESOURCE_TYPE.APPLICATION" :icon="row.source_icon" :size="20" />
            <ToolIcon v-else :icon="row.source_icon" :type="row.type" :size="20" />
            <span class="min-w-0 flex-1 truncate">{{ row.source_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="80"
        ><template #default="{ row }">{{ row.source_type === RESOURCE_TYPE.APPLICATION ? '智能体' : '工具' }}</template></el-table-column
      >
      <el-table-column label="状态" width="100"
        ><template #default="{ row }"><MkStatusLabel :status="row.state" /></template
      ></el-table-column>
      <el-table-column label="耗时" width="90"
        ><template #default="{ row }">{{ row.run_time == null ? '-' : `${row.run_time.toFixed(2)} s` }}</template></el-table-column
      >
      <el-table-column label="执行时间" prop="create_time" width="180"
        ><template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template></el-table-column
      >
      <el-table-column label="操作" width="70">
        <template #default="{ row }">
          <!-- 查看执行详情 -->
          <MkTooltip content="执行详情" placement="top">
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
