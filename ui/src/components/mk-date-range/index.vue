<script setup lang="ts">
import { ref } from 'vue'
import type { OptionItem } from '@/api/types'
import { beforeDay } from '@/utils/time'
import type { MkDateRangeValue } from './types'

defineOptions({ name: 'MkDateRange' })

type DatePreset = 7 | 30 | 90 | 183 | 'custom'

const emit = defineEmits<{ change: [value: MkDateRangeValue] }>()

const datePresetOptions: OptionItem<DatePreset>[] = [
  { label: '过去 7 天', value: 7 },
  { label: '过去 30 天', value: 30 },
  { label: '过去 90 天', value: 90 },
  { label: '过去半年', value: 183 },
  { label: '自定义', value: 'custom' },
]

const datePreset = ref<DatePreset>(7)
const customDateRange = ref<string[]>([])

function handleDatePresetChange(preset: DatePreset) {
  emit('change', { startTime: beforeDay(preset), endTime: '' })
}

function handleCustomDateRangeChange() {
  emit('change', { startTime: customDateRange.value[0] ?? '', endTime: customDateRange.value[1] ?? '' })
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
