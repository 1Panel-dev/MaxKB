<script setup lang="ts">
import { formatTokenNumber, numberFormat } from '@/utils/number'
import { computed, ref, watch } from 'vue'
import type { HomeMonitoringDay } from '@/api/types'
import type HomepageApi from '@/api/admin/workspace/homepage'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import MkLineChart from '@/components/mk-echart/LineCharts.vue'
import { beforeDay } from '@/utils/time'
const props = defineProps<{ workspaceId: string; applicationId: string; api: typeof HomepageApi }>()
defineSlots<{ application(props: { loading: boolean }): unknown }>()

/* 日期、智能体筛选与使用统计 */
const range = ref({ start_time: beforeDay(7), end_time: beforeDay(0) })
const loading = ref(false)
const monitoring = ref<HomeMonitoringDay[]>([])
const days = computed(() => monitoring.value.map((day) => day.day))
const metrics = computed(() =>
  [
    {
      id: 'activeUsers',
      title: '活跃用户',
      keys: [
        { key: 'customer_num', label: '活跃用户' },
        { key: 'customer_added_count', label: '新增用户' },
      ],
    },
    { id: 'conversations', title: '对话次数', keys: [{ key: 'chat_record_count', label: '对话次数' }] },
    { id: 'tokens', title: 'Tokens 总数', keys: [{ key: 'tokens_num', label: 'Tokens' }] },
    {
      id: 'feedback',
      title: '用户满意度',
      keys: [
        { key: 'star_num', label: '赞同' },
        { key: 'trample_num', label: '反对' },
      ],
    },
  ].map((metric) => ({
    ...metric,
    series: metric.keys.map(({ key, label }) => ({
      name: label,
      total: monitoring.value.reduce((sum, day) => sum + (Number(day[key as keyof HomeMonitoringDay]) || 0), 0),
      data: monitoring.value.map((day) => Number(day[key as keyof HomeMonitoringDay]) || 0),
    })),
  })),
)
function loadMonitoring() {
  loading.value = true
  return props.api
    .getMonitoring(props.workspaceId, range.value, props.applicationId === 'all' ? undefined : props.applicationId)
    .then((result) => {
      monitoring.value = result
    })
    .catch(() => {
      monitoring.value = []
    })
    .finally(() => {
      loading.value = false
    })
}
function handleRangeChange({ startTime, endTime }: MkDateRangeValue) {
  range.value = { start_time: startTime, end_time: endTime }
  loadMonitoring()
}
watch(() => [props.workspaceId, props.applicationId], loadMonitoring, { immediate: true })
</script>

<template>
  <section>
    <div class="mb-4 flex-align-center flex-wrap justify-between gap-3">
      <h4>监控</h4>
      <div class="flex flex-wrap gap-3">
        <MkDateRange @change="handleRangeChange" />

        <slot name="application" :loading="loading" />
      </div>
    </div>
    <div v-loading="loading" class="min-h-40">
      <div class="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <template v-for="metric in metrics" :key="metric.id">
          <el-card shadow="never">
            <p class="text-N600">{{ metric.title }}</p>
            <div class="mt-1 flex-align-center gap-4 tabular-nums">
              <template v-if="metric.id === 'feedback'">
                <template v-for="(series, index) in metric.series" :key="series.name">
                  <div class="flex-align-center gap-2" :title="series.name">
                    <MkIcon
                      :name="index === 0 ? 'icon_thumbsup_filled' : 'icon_thumbdown_filled'"
                      :size="16"
                      class="shrink-0"
                      :class="index === 0 ? 'text-[#FFCC00]!' : 'text-danger!'"
                    />
                    <h2>{{ numberFormat(series.total) }}</h2>
                  </div>
                </template>
              </template>
              <template v-else>
                <h2>
                  {{ metric.id === 'tokens' ? formatTokenNumber(metric.series[0]?.total) : numberFormat(metric.series[0]?.total) }}
                </h2>
                <span v-if="metric.id === 'activeUsers'" class="-ml-1 font-medium text-danger" title="新增用户"
                  >+{{ numberFormat(metric.series[1]?.total) }}</span
                >
              </template>
            </div>
          </el-card>
        </template>
      </div>
      <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <template v-for="metric in metrics" :key="metric.id">
          <el-card shadow="never">
            <h4>{{ metric.title }}</h4>
            <MkLineChart
              :value-formatter="metric.id === 'tokens' ? formatTokenNumber : numberFormat"
              class="-mt-6"
              :option="{ xData: days, yData: metric.series }"
              height="380px"
            />
          </el-card>
        </template>
      </div>
    </div>
  </section>
</template>
