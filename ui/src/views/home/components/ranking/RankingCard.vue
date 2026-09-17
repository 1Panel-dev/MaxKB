<script setup lang="ts">
import type { HomeRankingKind, HomeRankingRecord } from '@/api/types'
import { formatTokenNumber, numberFormat } from '@/utils/number'

const props = defineProps<{
  title: string
  kind: HomeRankingKind
  records?: HomeRankingRecord[]
  loading: boolean
  total?: number
}>()
defineEmits<{ detail: [] }>()
defineSlots<{ description(props: { record: HomeRankingRecord; index: number }): unknown }>()

function getRankingName(record: HomeRankingRecord) {
  return props.kind === 'userTokens' ? record.asker?.username : record.name
}
function getRecordPercentage(record: HomeRankingRecord) {
  const value = props.kind === 'questions' ? record.chat_record_count : (record.total_tokens ?? 0)
  const total = props.total ?? 0
  return total > 0 ? Math.min(100, Math.max(0, Number(((value / total) * 100).toFixed(1)))) : 0
}
</script>

<template>
  <el-card shadow="hover" class="min-h-99">
    <div class="mb-6 flex-between">
      <h4>{{ title }}</h4>
      <!-- 查看排行榜详情 -->
      <el-button text :disabled="loading" class="-mr-1" @click="$emit('detail')">
        <span>详情</span>
        <MkIcon name="icon_right_outlined" />
      </el-button>
    </div>
    <MkEmpty v-if="!loading && !records?.length" :image-size="80" />
    <div v-else class="space-y-6">
      <template v-for="(record, index) in records" :key="index">
        <div class="flex-between gap-3">
          <div class="flex min-w-0 flex-1 items-center gap-3">
            <span class="mk-rank shrink-0" :class="index < 3 ? `mk-rank-${index + 1}` : 'text-N600'">{{ index + 1 }}</span>
            <div class="min-w-0">
              <h6 class="truncate" :title="getRankingName(record)">{{ getRankingName(record) }}</h6>
              <p class="text-sm text-N600 flex items-center gap-2">
                <slot name="description" :record="record" :index="index" />
              </p>
            </div>
          </div>
          <div class="w-25 shrink-0">
            <el-progress :percentage="getRecordPercentage(record)" :show-text="false" :stroke-width="8" />
            <p class="color-secondary mt-4">
              {{ kind === 'questions' ? numberFormat(record.chat_record_count) : formatTokenNumber(record.total_tokens ?? 0) }}
            </p>
          </div>
        </div>
      </template>
    </div>
  </el-card>
</template>
