<script setup lang="ts">
import { useApplicationDetailContext } from '../../context'
import { computed, onMounted, ref } from 'vue'

import type { ApplicationRankingKind, HomeRankingRecord } from '@/api/types'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { beforeDay } from '@/utils/time'
import { formatTokenNumber, numberFormat } from '@/utils/number'
import RankingCard from '@/views/home/components/ranking/RankingCard.vue'
import ApplicationRankingDrawer from './ApplicationRankingDrawer.vue'

const { resourceApi } = useApplicationDetailContext()

defineOptions({ name: 'ApplicationRanking' })
const props = defineProps<{ applicationId: string }>()

/* TOP5 使用分页首屏，汇总数据独立查询。 */
const range = ref({ start_time: beforeDay(7), end_time: beforeDay(0) })
const loading = ref(false)
const tokenUsage = ref<HomeRankingRecord[]>()
const topQuestions = ref<HomeRankingRecord[]>()
const tokenTotal = ref<number>()
const chatTotal = ref<number>()
const rankingOptions = [
  { kind: 'userTokens', title: 'Tokens 消耗 · Top 用户' },
  { kind: 'questions', title: '对话次数 · Top 用户' },
] as const
const detailKind = ref<ApplicationRankingKind>()
function handleOpenRankingDetail(kind: ApplicationRankingKind) {
  detailKind.value = kind
}
const rankings = computed<Record<ApplicationRankingKind, HomeRankingRecord[] | undefined>>(() => ({
  userTokens: tokenUsage.value,
  questions: topQuestions.value?.map((record) => ({ ...record, name: record.asker?.username })),
}))
const totals = computed(() => ({
  userTokens: tokenTotal.value,
  questions: chatTotal.value,
}))
function loadRankings() {
  loading.value = true
  const query = { ...range.value }
  return Promise.allSettled([
    resourceApi.overview
      .getRanking(props.applicationId, 'userTokens', { currentPage: 1, pageSize: 5 }, query)
      .then((result) => {
        tokenUsage.value = result.records
      })
      .catch(() => {
        tokenUsage.value = undefined
      }),
    resourceApi.overview
      .getRanking(props.applicationId, 'questions', { currentPage: 1, pageSize: 5 }, query)
      .then((result) => {
        topQuestions.value = result.records
      })
      .catch(() => {
        topQuestions.value = undefined
      }),
    resourceApi.overview
      .getTokensAggregation(props.applicationId, query)
      .then((value) => {
        tokenTotal.value = value
      })
      .catch(() => {
        tokenTotal.value = undefined
      }),
    resourceApi.overview
      .getChatRecordAggregation(props.applicationId, query)
      .then((value) => {
        chatTotal.value = value
      })
      .catch(() => {
        chatTotal.value = undefined
      }),
  ]).finally(() => {
    loading.value = false
  })
}
function handleRangeChange({ startTime, endTime }: MkDateRangeValue) {
  range.value = { start_time: startTime, end_time: endTime }
  void loadRankings()
}
onMounted(loadRankings)
</script>

<template>
  <section>
    <div class="flex-between mb-4">
      <h4>排行榜 TOP5</h4>
      <MkDateRange @change="handleRangeChange" />
    </div>
    <div v-loading="loading" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <!-- 查看当前智能体的完整用户排行 -->
      <RankingCard
        v-for="option in rankingOptions"
        :key="option.kind"
        :title="option.title"
        :kind="option.kind"
        :records="rankings[option.kind]"
        :loading="loading"
        :total="totals[option.kind]"
        @detail="handleOpenRankingDetail(option.kind)"
      >
        <template #description="{ record }">
          <span v-if="option.kind === 'userTokens'">对话 {{ numberFormat(record.chat_record_count) }} 次</span>
          <span v-else>{{ formatTokenNumber(record.total_tokens ?? 0) }}</span>
        </template>
      </RankingCard>
    </div>
    <ApplicationRankingDrawer
      v-if="detailKind"
      :application-id="applicationId"
      :initial-kind="detailKind"
      :initial-range="range"
      @closed="detailKind = undefined"
    />
  </section>
</template>

<style scoped lang="scss"></style>
