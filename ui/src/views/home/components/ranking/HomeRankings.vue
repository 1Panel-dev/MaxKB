<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { HomeRankingKind, HomeRankingRecord } from '@/api/types'
import type HomepageApi from '@/api/admin/workspace/homepage'
import RankingDrawer from './RankingDrawer.vue'
import RankingCard from './RankingCard.vue'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { beforeDay } from '@/utils/time'
import { numberFormat, formatTokenNumber } from '@/utils/number'

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
onMounted(loadRankings)
</script>
<template>
  <section>
    <div class="flex-between mb-4">
      <h4>排行榜 TOP5</h4>
      <MkDateRange @change="handleRangeChange" />
    </div>
    <div v-loading="loading" class="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <RankingCard
        title="Tokens 消耗 · Top 智能体"
        :records="rankings.tokens"
        :loading="loading"
        kind="tokens"
        :total="tokenTotal"
        @detail="handleOpenRanking('tokens')"
      >
        <template #description="{ record }">
          <span>对话 {{ numberFormat(record.chat_record_count) }} 次 </span>
          <el-divider direction="vertical" />
          <span> 均 {{ formatTokenNumber(getRankingAverage('tokens', record)) }} Tokens </span>
        </template>
      </RankingCard>
      <RankingCard
        title="对话次数 · Top 智能体"
        :records="rankings.questions"
        :loading="loading"
        kind="questions"
        :total="chatTotal"
        @detail="handleOpenRanking('questions')"
      >
        <template #description="{ record }">
          <span>活跃用户 {{ numberFormat(record.chat_user_count) }} </span>
          <el-divider direction="vertical" />
          <span> 均 {{ numberFormat(getRankingAverage('questions', record)) }} 轮/人</span>
        </template>
      </RankingCard>
      <RankingCard
        title="Tokens 消耗 · Top 用户"
        :records="rankings.userTokens"
        :loading="loading"
        kind="userTokens"
        :total="tokenTotal"
        @detail="handleOpenRanking('userTokens')"
      >
        <template #description="{ record }"> 对话 {{ numberFormat(record.chat_record_count) }} 次 </template>
      </RankingCard>
    </div>
    <RankingDrawer :api="api" v-if="selectedKind" :workspace-id="workspaceId" :initial-kind="selectedKind" :initial-range="range" />
  </section>
</template>
