<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationRankingKind, HomeDateRange, HomeRankingRecord } from '@/api/types'
import type { MkDateRangeValue } from '@/components/global/mk-date-range/types'
import { useApplicationDetailContext } from '../../context'
import { formatTokenNumber, numberFormat } from '@/utils/number'
import { isSystemResource } from '@/utils/resource-context'
import perm from '@/permission'

defineOptions({ name: 'ApplicationRankingDrawer' })
const props = defineProps<{ applicationId: string; initialKind: ApplicationRankingKind; initialRange: HomeDateRange }>()
const emit = defineEmits<{ closed: [] }>()
const { t } = useI18n({ useScope: 'global' })

const { resourceApi } = useApplicationDetailContext()

/* 概览排行榜导出需要独立的概览导出权限。 */
const canExport = computed(() => {
  if (isSystemResource()) return Boolean(perm.application.system.overviewExport())
  return Boolean(perm.application.workspace.overviewExport(props.applicationId))
})

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
  <MkDrawer
    v-model="visible"
    :title="t('overview.ranking.detailTitle')"
    class="mk-drawer-with-tabs"
    contentClass="pt-0"
    size="1000"
    @closed="emit('closed')"
  >
    <el-tabs v-model="activeKind" @tab-change="handleTabChange">
      <el-tab-pane name="userTokens" :label="t('overview.ranking.userTokens')" />
      <el-tab-pane name="questions" :label="t('overview.ranking.userConversations')" />
    </el-tabs>
    <div class="mt-6 mb-4 flex-between">
      <div class="flex gap-3">
        <MkDateRange :default-value="{ startTime: initialRange.start_time, endTime: initialRange.end_time }" @change="handleRangeChange" />
        <MkSearchInput v-model="searchName" class="w-55!" @change="handleSearch" />
      </div>
      <!-- 导出当前筛选下的完整用户排行 -->
      <el-button v-if="canExport" plain :loading="exporting" :disabled="loading" @click="handleExport">
        <MkIcon name="icon_export_outlined" />
        <span>{{ t('common.actions.export') }}</span>
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
      <el-table-column :label="t('overview.ranking.rank')" width="60">
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
      <el-table-column :label="t('overview.ranking.user')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.asker?.username || '-' }}</template>
      </el-table-column>
      <el-table-column
        :label="activeKind === 'userTokens' ? t('overview.ranking.tokenUsage') : t('overview.monitoring.conversations')"
        min-width="125"
      >
        <template #default="{ row }">
          {{ formatRankingValue(row) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="activeKind === 'userTokens' ? t('overview.monitoring.conversations') : t('overview.ranking.tokenUsage')"
        min-width="125"
      >
        <template #default="{ row }">
          {{ formatRankingValue(row, activeKind === 'userTokens' ? 'questions' : 'userTokens') }}
        </template>
      </el-table-column>
      <el-table-column :label="t('overview.ranking.percentage')" min-width="150">
        <template #default="{ row }">
          <el-progress v-if="aggregateTotal != null && getRankingValue(row) != null" :percentage="getRankingRatio(row)" />
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('overview.ranking.tokensPerChat')" min-width="125">
        <template #default="{ row }">{{ formatTokenNumber(getRankingAverage(row)) }}</template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
</template>
