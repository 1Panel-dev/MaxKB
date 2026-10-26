<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { ApplicationRankingKind, HomeDateRange, HomeRankingRecord } from '@/api/types'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { formatTokenNumber, numberFormat } from '@/utils/number'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'ApplicationRankingDrawer' })
const props = defineProps<{ applicationId: string; initialKind: ApplicationRankingKind; initialRange: HomeDateRange }>()
const emit = defineEmits<{ closed: [] }>()
const { resourceApi } = useApplicationDetailContext()

const visible = ref(true)
const activeKind = ref(props.initialKind)
const loading = ref(false)
const exporting = ref(false)
const range = ref({ ...props.initialRange })
const searchName = ref('')
const records = ref<HomeRankingRecord[]>([])
const aggregateTotal = ref<number>()
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })

function getRankingValue(record: HomeRankingRecord, kind = activeKind.value) {
  return kind === 'questions' ? record.chat_record_count : record.total_tokens
}
function formatRankingValue(record: HomeRankingRecord, kind = activeKind.value) {
  const value = getRankingValue(record, kind)
  if (value == null) return '—'
  return kind === 'userTokens' ? formatTokenNumber(value) : numberFormat(value)
}
function getRankingRatio(record: HomeRankingRecord) {
  const total = aggregateTotal.value ?? 0
  return total > 0 ? Math.min(100, Math.max(0, Number((((getRankingValue(record) ?? 0) / total) * 100).toFixed(1)))) : 0
}
function getRankingAverage(record: HomeRankingRecord) {
  if (record.total_tokens == null || record.chat_record_count == null) return undefined
  return record.chat_record_count > 0 ? record.total_tokens / record.chat_record_count : 0
}

/* 分页与汇总分别查询，搜索不改变同期占比的分母。 */
function loadRanking() {
  if (loading.value) return
  loading.value = true
  const kind = activeKind.value
  const query = { ...range.value }
  return Promise.allSettled([
    resourceApi.overview
      .getRanking(props.applicationId, kind, pagination.value, query, searchName.value.trim())
      .then((result) => {
        records.value = result.records
        pagination.value.total = result.total
      })
      .catch(() => {
        records.value = []
        pagination.value.total = 0
      }),
    (kind === 'questions'
      ? resourceApi.overview.getChatRecordAggregation(props.applicationId, query)
      : resourceApi.overview.getTokensAggregation(props.applicationId, query)
    )
      .then((value) => {
        aggregateTotal.value = value
      })
      .catch(() => {
        aggregateTotal.value = undefined
      }),
  ]).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  pagination.value.currentPage = 1
  return loadRanking()
}
function handleTabChange() {
  searchName.value = ''
  return handleSearch()
}
function handleRangeChange({ startTime, endTime }: MkDateRangeValue) {
  range.value = { start_time: startTime, end_time: endTime }
  return handleSearch()
}
function handleExport() {
  exporting.value = true
  return resourceApi.overview.exportRanking(props.applicationId, activeKind.value, range.value, searchName.value.trim()).finally(() => {
    exporting.value = false
  })
}

onMounted(loadRanking)
</script>

<template>
  <MkDrawer v-model="visible" title="排行榜详情" size="1000" @closed="emit('closed')">
    <div :inert="loading">
      <el-tabs v-model="activeKind" @tab-change="handleTabChange">
        <el-tab-pane name="userTokens" label="Tokens 消耗 · Top 用户" />
        <el-tab-pane name="questions" label="对话次数 · Top 用户" />
      </el-tabs>
      <div class="my-4 flex-between">
        <div class="flex gap-3">
          <MkSearchInput v-model="searchName" class="w-55!" @change="handleSearch" />
          <MkDateRange :default-value="{ startTime: initialRange.start_time, endTime: initialRange.end_time }" @change="handleRangeChange" />
        </div>
        <!-- 导出当前筛选下的完整用户排行 -->
        <el-button plain :loading="exporting" :disabled="loading" @click="handleExport">
          <MkIcon name="icon_export_outlined" />
          <span>导出</span>
        </el-button>
      </div>
      <MkTable
        v-loading="loading"
        v-model:pagination-config="pagination"
        :data="records"
        row-key="chat_user_id"
        @current-change="loadRanking"
        @size-change="loadRanking"
      >
        <el-table-column label="排名" width="60">
          <template #default="{ $index }">
            <span
              class="mk-rank"
              :class="
                (pagination.currentPage - 1) * pagination.pageSize + $index < 3
                  ? `mk-rank-${(pagination.currentPage - 1) * pagination.pageSize + $index + 1}`
                  : 'text-N600'
              "
            >
              {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="用户" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.asker?.username || '-' }}</template>
        </el-table-column>
        <el-table-column :label="activeKind === 'userTokens' ? 'Tokens 消耗' : '对话次数'" min-width="125">
          <template #default="{ row }">
            {{ formatRankingValue(row) }}
          </template>
        </el-table-column>
        <el-table-column label="占比" min-width="150">
          <template #default="{ row }">
            <el-progress v-if="aggregateTotal != null && getRankingValue(row) != null" :percentage="getRankingRatio(row)" />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column :label="activeKind === 'userTokens' ? '对话次数' : 'Tokens 消耗'" min-width="125">
          <template #default="{ row }">
            {{ formatRankingValue(row, activeKind === 'userTokens' ? 'questions' : 'userTokens') }}
          </template>
        </el-table-column>
        <el-table-column label="均 Tokens/次" min-width="125">
          <template #default="{ row }">{{ formatTokenNumber(getRankingAverage(row)) }}</template>
        </el-table-column>
      </MkTable>
    </div>
  </MkDrawer>
</template>
