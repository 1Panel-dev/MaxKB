<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { HomeDateRange, HomeRankingKind, HomeRankingRecord } from '@/api/types'
import type HomepageApi from '@/api/admin/workspace/homepage'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { numberFormat, formatTokenNumber } from '@/utils/number'

const props = defineProps<{ api: typeof HomepageApi; workspaceId: string; initialKind: HomeRankingKind; initialRange: HomeDateRange }>()

/* 排行类型与展示计算 */

function getRankingValue(kind: HomeRankingKind, record: HomeRankingRecord) {
  return kind === 'questions' ? record.chat_record_count : (record.total_tokens ?? 0)
}
function getRankingRatio(value: number, total: number) {
  return total > 0 ? Math.min(100, Math.max(0, Number(((value / total) * 100).toFixed(1)))) : 0
}
function getRankingAverage(kind: HomeRankingKind, record: HomeRankingRecord) {
  const count = kind === 'questions' ? (record.chat_user_count ?? 0) : record.chat_record_count
  return count > 0 ? Number((getRankingValue(kind, record) / count).toFixed(1)) : 0
}

/* 抽屉筛选、分页与排行查询 */
const visible = ref(true)
const activeKind = ref(props.initialKind)
const range = ref({ ...props.initialRange })
const searchName = ref('')
const loading = ref(false)
const exporting = ref(false)
const records = ref<HomeRankingRecord[]>([])
const aggregateTotal = ref<number>(0)
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })

function loadRanking() {
  loading.value = true
  const kind = activeKind.value
  const query = { ...range.value }
  return Promise.allSettled([
    props.api
      .getRanking(props.workspaceId, kind, pagination.value, query, searchName.value.trim())
      .then((result) => {
        records.value = result.records
        pagination.value.total = result.total
      })
      .catch(() => {
        records.value = []
        pagination.value.total = 0
      }),
    (kind === 'questions' ? props.api.getChatRecordAggregation(props.workspaceId, query) : props.api.getTokensAggregation(props.workspaceId, query))
      .then((value) => {
        aggregateTotal.value = value
      })
      .catch(() => {
        aggregateTotal.value = 0
      }),
  ]).finally(() => {
    loading.value = false
  })
}
function handleSearch() {
  pagination.value.currentPage = 1
  loadRanking()
}
function handleTabChange() {
  searchName.value = ''
  handleSearch()
}
function handleRangeChange({ startTime, endTime }: MkDateRangeValue) {
  range.value = { start_time: startTime, end_time: endTime }
  handleSearch()
}
/* 导出当前筛选范围内的完整排行 */
function handleExport() {
  exporting.value = true
  return props.api.exportRanking(props.workspaceId, activeKind.value, range.value, searchName.value.trim()).finally(() => {
    exporting.value = false
  })
}
onMounted(() => loadRanking())
</script>
<template>
  <MkDrawer v-model="visible" title="排行榜详情" size="1000">
    <el-tabs v-model="activeKind" @tab-change="handleTabChange">
      <el-tab-pane name="tokens" label="Tokens 消耗 · Top 智能体" />
      <el-tab-pane name="questions" label="提问次数 · Top 智能体" />
      <el-tab-pane name="userTokens" label="Tokens 消耗 · Top 用户" />
    </el-tabs>
    <div class="my-4 flex-between">
      <div class="flex gap-3">
        <MkSearchInput v-model="searchName" class="w-55!" @change="handleSearch" />
        <MkDateRange :default-value="{ startTime: initialRange.start_time, endTime: initialRange.end_time }" @change="handleRangeChange" />
      </div>
      <!-- 导出当前筛选下的完整排行榜 -->
      <el-button plain :loading="exporting" :disabled="loading" @click="handleExport">导出</el-button>
    </div>

    <MkTable v-loading="loading" v-model:pagination-config="pagination" :data="records" @current-change="loadRanking" @size-change="handleSearch">
      <el-table-column label="排名" width="60">
        <template #default="{ $index }">
          <span
            class="mk-rank shrink-0"
            :class="
              (pagination.currentPage - 1) * pagination.pageSize + $index < 3
                ? `mk-rank-${(pagination.currentPage - 1) * pagination.pageSize + $index + 1}`
                : 'text-N600'
            "
            >{{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}</span
          >
        </template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'userTokens'" label="用户" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.asker?.username || '-' }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'questions'" label="智能体名称" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">{{ row.name || '-' }}</template>
      </el-table-column>

      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'userTokens'" label="Tokens 消耗" min-width="125">
        <template #default="{ row }">{{ formatTokenNumber(row.total_tokens ?? 0) }}</template>
      </el-table-column>
      <el-table-column label="占比" min-width="150">
        <template #default="{ row }">
          <el-progress :percentage="getRankingRatio(getRankingValue(activeKind, row), aggregateTotal)" />
        </template>
      </el-table-column>

      <el-table-column label="对话轮次" min-width="100">
        <template #default="{ row }">{{ numberFormat(row.chat_record_count) }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'questions'" label="活跃用户" min-width="100">
        <template #default="{ row }">{{ numberFormat(row.chat_user_count) }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'questions'" label="人均对话轮次" min-width="135">
        <template #default="{ row }">{{ numberFormat(getRankingAverage('questions', row)) }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'userTokens'" label="均 Tokens/轮" min-width="105">
        <template #default="{ row }">{{ formatTokenNumber(getRankingAverage(activeKind, row)) }}</template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
</template>
