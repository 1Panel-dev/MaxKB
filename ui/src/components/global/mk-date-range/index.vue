<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MkDateRangeValue } from './types'
import type { OptionItem } from '@/api/types'
import { beforeDay } from '@/utils/time'

defineOptions({ name: 'MkDateRange' })

const { t } = useI18n({ useScope: 'global' })

type DatePreset = 7 | 30 | 90 | 183 | 'custom'

const props = defineProps<{ defaultValue?: MkDateRangeValue }>()
const emit = defineEmits<{ change: [value: MkDateRangeValue] }>()

const datePresetOptions = computed<OptionItem<DatePreset>[]>(() => [
  { label: t('common.dateRange.lastDays', { days: 7 }), value: 7 },
  { label: t('common.dateRange.lastDays', { days: 30 }), value: 30 },
  { label: t('common.dateRange.lastDays', { days: 90 }), value: 90 },
  { label: t('common.dateRange.lastHalfYear'), value: 183 },
  { label: t('common.dateRange.custom'), value: 'custom' },
])

/* 默认范围只在挂载时回填，不触发查询。 */
const initialRange = props.defaultValue ?? { startTime: beforeDay(7), endTime: beforeDay(0) }
const initialEndTime = initialRange.endTime || beforeDay(0)
const datePreset = ref<DatePreset>(
  datePresetOptions.value.find(({ value }) => value !== 'custom' && initialRange.startTime === beforeDay(value) && initialEndTime === beforeDay(0))
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
    <el-select v-model="datePreset" class="w-36!" @change="handleDatePresetChange">
      <el-option v-for="option in datePresetOptions" :key="option.value" :label="option.label" :value="option.value" />
    </el-select>
    <el-date-picker
      v-if="datePreset === 'custom'"
      v-model="customDateRange"
      class="w-72!"
      type="daterange"
      :start-placeholder="t('common.dateRange.startDate')"
      :end-placeholder="t('common.dateRange.endDate')"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      @change="handleCustomDateRangeChange"
    />
  </div>
</template>
