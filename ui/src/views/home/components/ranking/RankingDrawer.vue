<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type HomepageApi from '@/api/admin/workspace/homepage'
import type { HomeDateRange, HomeRankingKind, HomeRankingRecord } from '@/api/types'
import type { MkDateRangeValue } from '@/components/global/mk-date-range/types'
import { formatTokenNumber, numberFormat } from '@/utils/number'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const route = useRoute()
const isSystemHome = computed(() => route.meta.scope === 'system')

/* 排行榜导出权限：系统概览走系统首页权限，工作空间概览走概览权限 */
const canExport = computed(() => (isSystemHome.value ? Boolean(perm.system.homepage.export()) : Boolean(perm.homepage.homepage.export())))

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
  <MkDrawer v-model="visible" :title="t('overview.ranking.detailTitle')" class="mk-drawer-with-tabs" contentClass="pt-0" size="1000">
    <el-tabs v-model="activeKind" @tab-change="handleTabChange">
      <el-tab-pane name="tokens" :label="t('overview.ranking.agentTokens')" />
      <el-tab-pane name="questions" :label="t('overview.ranking.agentConversations')" />
      <el-tab-pane name="userTokens" :label="t('overview.ranking.userTokens')" />
    </el-tabs>
    <div class="mt-6 mb-4 flex-between">
      <div class="flex gap-3">
        <MkDateRange :default-value="{ startTime: initialRange.start_time, endTime: initialRange.end_time }" @change="handleRangeChange" />
        <MkSearchInput v-model="searchName" class="w-55!" @change="handleSearch" />
      </div>
      <!-- 导出当前筛选下的完整排行榜 -->
      <el-button v-if="canExport" plain :loading="exporting" :disabled="loading" @click="handleExport">
        <MkIcon name="icon_export_outlined" />
        <span>{{ t('common.actions.export') }}</span>
      </el-button>
    </div>

    <MkTable v-loading="loading" v-model:pagination-config="pagination" :data="records" @current-change="loadRanking" @size-change="handleSearch">
      <el-table-column :label="t('overview.ranking.rank')" width="60">
        <template #default="{ $index }">
          <span
            class="mk-rank shrink-0"
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
      <el-table-column v-if="activeKind === 'userTokens'" :label="t('overview.ranking.user')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.asker?.username || '-' }}</template>
      </el-table-column>
      <el-table-column
        v-if="activeKind === 'tokens' || activeKind === 'questions'"
        :label="t('overview.ranking.applicationName')"
        min-width="150"
        show-overflow-tooltip
      >
        <template #default="{ row }">{{ row.name || '-' }}</template>
      </el-table-column>

      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'userTokens'" :label="t('overview.ranking.tokenUsage')" min-width="125">
        <template #default="{ row }">{{ formatTokenNumber(row.total_tokens ?? 0) }}</template>
      </el-table-column>
      <el-table-column :label="t('overview.monitoring.conversations')" min-width="100">
        <template #default="{ row }">{{ numberFormat(row.chat_record_count) }}</template>
      </el-table-column>
      <el-table-column :label="t('overview.ranking.percentage')" min-width="150">
        <template #default="{ row }">
          <el-progress :percentage="getRankingRatio(getRankingValue(activeKind, row), aggregateTotal)" />
        </template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'questions'" :label="t('overview.monitoring.activeUsers')" min-width="100">
        <template #default="{ row }">{{ numberFormat(row.chat_user_count) }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'questions'" :label="t('overview.ranking.roundsPerUser')" min-width="135">
        <template #default="{ row }">{{ numberFormat(getRankingAverage('questions', row)) }}</template>
      </el-table-column>
      <el-table-column v-if="activeKind === 'tokens' || activeKind === 'userTokens'" :label="t('overview.ranking.tokensPerRound')" min-width="135">
        <template #default="{ row }">{{ formatTokenNumber(getRankingAverage(activeKind, row)) }}</template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
</template>
