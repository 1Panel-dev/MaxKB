<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type HomepageApi from '@/api/admin/workspace/homepage'
import type { HomeRankingKind, HomeRankingRecord } from '@/api/types'
import type { MkDateRangeValue } from '@/components/global/mk-date-range/types'
import RankingCard from './RankingCard.vue'
import RankingDrawer from './RankingDrawer.vue'
import { formatTokenNumber, numberFormat } from '@/utils/number'
import { beforeDay } from '@/utils/time'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ workspaceId: string; api: typeof HomepageApi }>()

/* 排行类型与展示计算 */

function getRankingValue(kind: HomeRankingKind, record: HomeRankingRecord) {
  return kind === 'questions' ? record.chat_record_count : (record.total_tokens ?? 0)
}
function getRankingAverage(kind: HomeRankingKind, record: HomeRankingRecord) {
  const count = kind === 'questions' ? (record.chat_user_count ?? 0) : record.chat_record_count
  return count > 0 ? Number((getRankingValue(kind, record) / count).toFixed(1)) : 0
}

/* 排行榜查询与详情入口 */
const range = ref({ start_time: beforeDay(7), end_time: beforeDay(0) })
const loading = ref(false)
const tokenTotal = ref<number>()
const chatTotal = ref<number>()
const rankings = ref<Record<HomeRankingKind, HomeRankingRecord[] | undefined>>({ tokens: undefined, questions: undefined, userTokens: undefined })
const selectedKind = ref<HomeRankingKind>()
function loadRankings() {
  loading.value = true
  const query = { ...range.value }
  return Promise.allSettled([
    props.api
      .getTokensAggregation(props.workspaceId, query)
      .then((value) => {
        tokenTotal.value = value
      })
      .catch(() => {
        tokenTotal.value = undefined
      }),
    props.api
      .getChatRecordAggregation(props.workspaceId, query)
      .then((value) => {
        chatTotal.value = value
      })
      .catch(() => {
        chatTotal.value = undefined
      }),
    props.api
      .getRanking(props.workspaceId, 'tokens', { currentPage: 1, pageSize: 5 }, query)
      .then((result) => {
        rankings.value.tokens = result.records
      })
      .catch(() => {
        rankings.value.tokens = undefined
      }),
    props.api
      .getRanking(props.workspaceId, 'questions', { currentPage: 1, pageSize: 5 }, query)
      .then((result) => {
        rankings.value.questions = result.records
      })
      .catch(() => {
        rankings.value.questions = undefined
      }),
    props.api
      .getRanking(props.workspaceId, 'userTokens', { currentPage: 1, pageSize: 5 }, query)
      .then((result) => {
        rankings.value.userTokens = result.records
      })
      .catch(() => {
        rankings.value.userTokens = undefined
      }),
  ]).finally(() => {
    loading.value = false
  })
}
function handleRangeChange({ startTime, endTime }: MkDateRangeValue) {
  range.value = { start_time: startTime, end_time: endTime }
  loadRankings()
}
function handleOpenRanking(kind: HomeRankingKind) {
  selectedKind.value = kind
}
function handleRankingDrawerClosed() {
  selectedKind.value = undefined
}
onMounted(loadRankings)
</script>
<template>
  <section>
    <div class="flex-between mb-4">
      <h4>{{ t('overview.ranking.title') }} TOP5</h4>
      <MkDateRange @change="handleRangeChange" />
    </div>
    <div class="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <RankingCard
        :title="t('overview.ranking.agentTokens')"
        :records="rankings.tokens"
        :loading="loading"
        kind="tokens"
        :total="tokenTotal"
        @detail="handleOpenRanking('tokens')"
      >
        <template #description="{ record }">
          <span>{{ t('overview.ranking.conversationCount', { count: numberFormat(record.chat_record_count) }) }}</span>
          <el-divider direction="vertical" />
          <span>{{ t('overview.ranking.averageTokens', { count: formatTokenNumber(getRankingAverage('tokens', record)) }) }}</span>
        </template>
      </RankingCard>
      <RankingCard
        :title="t('overview.ranking.agentConversations')"
        :records="rankings.questions"
        :loading="loading"
        kind="questions"
        :total="chatTotal"
        @detail="handleOpenRanking('questions')"
      >
        <template #description="{ record }">
          <span>{{ t('overview.monitoring.activeUsers') }} {{ numberFormat(record.chat_user_count) }}</span>
          <el-divider direction="vertical" />
          <span>
            {{
              t(
                'overview.ranking.averageRounds',
                { count: numberFormat(getRankingAverage('questions', record)) },
                getRankingAverage('questions', record),
              )
            }}
          </span>
        </template>
      </RankingCard>
      <RankingCard
        :title="t('overview.ranking.userTokens')"
        :records="rankings.userTokens"
        :loading="loading"
        kind="userTokens"
        :total="tokenTotal"
        @detail="handleOpenRanking('userTokens')"
      >
        <template #description="{ record }">
          {{ t('overview.ranking.conversationCount', { count: numberFormat(record.chat_record_count) }) }}
        </template>
      </RankingCard>
    </div>
    <RankingDrawer
      v-if="selectedKind"
      :api="api"
      :workspace-id="workspaceId"
      :initial-kind="selectedKind"
      :initial-range="range"
      @closed="handleRankingDrawerClosed"
    />
  </section>
</template>
