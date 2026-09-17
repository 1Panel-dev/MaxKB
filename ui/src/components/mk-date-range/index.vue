<script setup lang="ts">
import { ref } from 'vue'
import type { OptionItem } from '@/api/types'
import { beforeDay } from '@/utils/time'
import type { MkDateRangeValue } from './types'

defineOptions({ name: 'MkDateRange' })

type DatePreset = 7 | 30 | 90 | 183 | 'custom'

const props = defineProps<{ defaultValue?: MkDateRangeValue }>()
const emit = defineEmits<{ change: [value: MkDateRangeValue] }>()

const datePresetOptions: OptionItem<DatePreset>[] = [
  { label: '过去 7 天', value: 7 },
  { label: '过去 30 天', value: 30 },
  { label: '过去 90 天', value: 90 },
  { label: '过去半年', value: 183 },
  { label: '自定义', value: 'custom' },
]

/* 默认范围只在挂载时回填，不触发查询。 */
const initialRange = props.defaultValue ?? { startTime: beforeDay(7), endTime: beforeDay(0) }
const initialEndTime = initialRange.endTime || beforeDay(0)
const datePreset = ref<DatePreset>(
  datePresetOptions.find(({ value }) => value !== 'custom' && initialRange.startTime === beforeDay(value) && initialEndTime === beforeDay(0))
    ?.value ?? 'custom',
)
const customDateRange = ref<string[] | null>(initialRange.startTime ? [initialRange.startTime, initialEndTime] : [])

function handleDatePresetChange(preset: DatePreset) {
  if (preset === 'custom') return
  const startTime = beforeDay(preset)
  const endTime = beforeDay(0)
  customDateRange.value = [startTime, endTime]
  emit('change', { startTime, endTime })
}

function handleCustomDateRangeChange() {
  emit('change', { startTime: customDateRange.value?.[0] ?? '', endTime: customDateRange.value?.[1] || beforeDay(0) })
}
</script>

<template>
  <div class="flex gap-3">
    <el-select v-model="datePreset" class="w-30!" @change="handleDatePresetChange">
      <el-option v-for="option in datePresetOptions" :key="option.value" :label="option.label" :value="option.value" />
    </el-select>
    <el-date-picker
      v-if="datePreset === 'custom'"
      v-model="customDateRange"
      class="w-72!"
      type="daterange"
      start-placeholder="开始日期"
      end-placeholder="结束日期"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      @change="handleCustomDateRangeChange"
    />
  </div>
</template>
