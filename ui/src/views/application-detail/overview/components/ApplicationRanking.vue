<script setup lang="ts">
import { useApplicationDetailContext } from '../../context'
import { computed, onMounted, ref } from 'vue'

import type { ApplicationTokenUsage, ApplicationTopQuestion, HomeRankingRecord } from '@/api/types'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { beforeDay } from '@/utils/time'
import RankingCard from '@/views/home/components/ranking/RankingCard.vue'

const { resourceApi } = useApplicationDetailContext()

defineOptions({ name: 'ApplicationRanking' })
const props = defineProps<{ applicationId: string }>()

/* 当前智能体的用户排行，接口返回完整数组。 */
const range = ref({ start_time: beforeDay(7), end_time: beforeDay(0) })
const loading = ref(false)
const tokenUsage = ref<ApplicationTokenUsage[]>()
const topQuestions = ref<ApplicationTopQuestion[]>()
const rankingOptions = [
  { kind: 'userTokens', title: 'Tokens 消耗 · Top 用户' },
  { kind: 'questions', title: '对话次数 · Top 用户' },
] as const
const rankings = computed<{ userTokens: HomeRankingRecord[] | undefined; questions: HomeRankingRecord[] | undefined }>(() => ({
  userTokens: tokenUsage.value?.map((record) => ({
    asker: { username: record.username },
    total_tokens: record.token_usage ?? 0,
    chat_record_count: 0,
  })),
  questions: topQuestions.value?.map((record) => ({ name: record.username, chat_record_count: record.chat_record_count })),
}))
const totals = computed(() => ({
  userTokens: tokenUsage.value?.reduce((total, record) => total + (record.token_usage ?? 0), 0),
  questions: topQuestions.value?.reduce((total, record) => total + record.chat_record_count, 0),
}))
function loadRankings() {
  loading.value = true
  return Promise.allSettled([
    resourceApi.overview
      .getTokenUsage(props.applicationId, range.value)
      .then((records) => {
        tokenUsage.value = records
      })
      .catch(() => {
        tokenUsage.value = undefined
      }),
    resourceApi.overview
      .getTopQuestions(props.applicationId, range.value)
      .then((records) => {
        topQuestions.value = records
      })
      .catch(() => {
        topQuestions.value = undefined
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
      <RankingCard
        v-for="option in rankingOptions"
        :key="option.kind"
        :title="option.title"
        :kind="option.kind"
        :records="rankings[option.kind]?.slice(0, 5)"
        :loading="loading"
        :total="totals[option.kind]"
      />
    </div>
  </section>
</template>

<style scoped lang="scss"></style>
