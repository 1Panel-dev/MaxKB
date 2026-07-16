<template>
  <el-dialog
    align-center
    :title="dialogTitle"
    v-model="dialogVisible"
    :width="dialogWidth"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <div v-if="state === 'config'">
      <div class="mb-16">
        <h4 class="mb-8">{{ $t('views.applicationOverview.ExportLogDialog.selectTimeRange') }}</h4>
        <div class="flex align-center">
          <el-select v-model="historyDay" class="w-180 mr-12" @change="changeDayHandle">
            <el-option
              v-for="item in dayOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-date-picker
            v-if="historyDay === 'other'"
            v-model="daterangeValue"
            type="daterange"
            :start-placeholder="$t('views.applicationOverview.ExportLogDialog.startDate')"
            :end-placeholder="$t('views.applicationOverview.ExportLogDialog.endDate')"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="changeDayRangeHandle"
          />
        </div>
      </div>

      <div class="mb-16">
        <div class="flex align-center mb-8">
          <h4>{{ $t('views.applicationOverview.ExportLogDialog.selectFields') }}</h4>
          <el-button link type="primary" class="ml-12" @click="toggleSelectAll">
            {{ selectAll ? $t('views.applicationOverview.ExportLogDialog.deselectAll') : $t('views.applicationOverview.ExportLogDialog.selectAll') }}
          </el-button>
        </div>
        <div v-for="group in fieldGroups" :key="group.key" class="mb-12">
          <div class="mb-4 field-group-title">{{ group.label }}</div>
          <el-checkbox-group v-model="selectedFields">
            <el-checkbox
              v-for="f in group.fields"
              :key="f.key"
              :label="f.key"
              class="mr-16"
            >
              {{ f.label }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
    </div>

    <div v-else-if="state === 'progress'" class="text-center">
      <el-progress :percentage="progress" :stroke-width="8" class="mb-16" />
      <p class="mb-8 text-gray">{{ progressText }}</p>
      <p class="mb-16 text-gray text-sm">{{ estimatedText }}</p>
    </div>

    <div v-else-if="state === 'failed'" class="text-center">
      <el-icon class="mb-12" :size="48" color="var(--el-color-danger)">
        <WarningFilled />
      </el-icon>
      <p class="mb-16">{{ errorMessage }}</p>
    </div>

    <template #footer>
      <div v-if="state === 'config'">
        <el-button @click="closeDialog">{{ $t('views.applicationOverview.ExportLogDialog.cancel') }}</el-button>
        <el-button
          type="primary"
          :disabled="!isFormValid || isExporting"
          :loading="isExporting"
          @click="startExport"
        >
          {{ $t('views.applicationOverview.ExportLogDialog.confirmExport') }}
        </el-button>
      </div>
      <div v-else-if="state === 'progress'">
        <el-button @click="cancelExport">{{ $t('views.applicationOverview.ExportLogDialog.cancelExport') }}</el-button>
      </div>
      <div v-else-if="state === 'failed'">
        <el-button @click="resetToConfig">{{ $t('views.applicationOverview.ExportLogDialog.cancel') }}</el-button>
        <el-button type="primary" @click="retryExport">{{ $t('views.applicationOverview.ExportLogDialog.retry') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import moment from 'moment'
import { nowDate, beforeDay } from '@/utils/time'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { WarningFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  id: string
  apiType: string
}>()

const emit = defineEmits<{
  refresh: []
}>()

const dialogVisible = ref(false)
const state = ref<'config' | 'progress' | 'failed'>('config')

const historyDay = ref<number | string>(7)
const daterangeValue = ref('')
const daterange = ref({ start_time: '', end_time: '' })

const dayOptions = [
  { value: 7, label: t('views.applicationOverview.ExportLogDialog.past7Days') },
  { value: 30, label: t('views.applicationOverview.ExportLogDialog.past30Days') },
  { value: 'month', label: t('views.applicationOverview.ExportLogDialog.thisMonth') },
  { value: 'other', label: t('views.applicationOverview.ExportLogDialog.customTime') },
]

const fieldGroups = [
  {
    key: 'sessionInfo',
    label: t('views.applicationOverview.ExportLogDialog.fieldGroups.sessionInfo'),
    fields: [
      { key: 'session_id', label: t('views.applicationOverview.ExportLogDialog.fields.session_id') },
      { key: 'user_id', label: t('views.applicationOverview.ExportLogDialog.fields.user_id') },
      { key: 'user_name', label: t('views.applicationOverview.ExportLogDialog.fields.user_name') },
      { key: 'chat_time', label: t('views.applicationOverview.ExportLogDialog.fields.chat_time') },
    ],
  },
  {
    key: 'conversationContent',
    label: t('views.applicationOverview.ExportLogDialog.fieldGroups.conversationContent'),
    fields: [
      { key: 'user_question', label: t('views.applicationOverview.ExportLogDialog.fields.user_question') },
      { key: 'ai_answer', label: t('views.applicationOverview.ExportLogDialog.fields.ai_answer') },
      { key: 'chat_round', label: t('views.applicationOverview.ExportLogDialog.fields.chat_round') },
    ],
  },
  {
    key: 'consumptionStats',
    label: t('views.applicationOverview.ExportLogDialog.fieldGroups.consumptionStats'),
    fields: [
      { key: 'input_tokens', label: t('views.applicationOverview.ExportLogDialog.fields.input_tokens') },
      { key: 'output_tokens', label: t('views.applicationOverview.ExportLogDialog.fields.output_tokens') },
      { key: 'total_tokens', label: t('views.applicationOverview.ExportLogDialog.fields.total_tokens') },
      { key: 'cost', label: t('views.applicationOverview.ExportLogDialog.fields.cost') },
    ],
  },
  {
    key: 'systemInfo',
    label: t('views.applicationOverview.ExportLogDialog.fieldGroups.systemInfo'),
    fields: [
      { key: 'model_name', label: t('views.applicationOverview.ExportLogDialog.fields.model_name') },
      { key: 'knowledge_calls', label: t('views.applicationOverview.ExportLogDialog.fields.knowledge_calls') },
      { key: 'response_time', label: t('views.applicationOverview.ExportLogDialog.fields.response_time') },
      { key: 'error_code', label: t('views.applicationOverview.ExportLogDialog.fields.error_code') },
    ],
  },
]

const allFieldKeys = fieldGroups.flatMap(g => g.fields.map(f => f.key))
const defaultFieldKeys = [
  'session_id', 'user_id', 'user_name', 'chat_time',
  'user_question', 'ai_answer', 'chat_round',
  'input_tokens', 'output_tokens', 'total_tokens', 'cost',
]
const selectedFields = ref<string[]>([...defaultFieldKeys])

const selectAll = computed(() => selectedFields.value.length === allFieldKeys.length)

function toggleSelectAll() {
  if (selectAll.value) {
    selectedFields.value = []
  } else {
    selectedFields.value = [...allFieldKeys]
  }
}

const isFormValid = computed(() => {
  return daterange.value.start_time && daterange.value.end_time && selectedFields.value.length > 0
})

const isExporting = ref(false)

function changeDayHandle(val: number | string) {
  if (val === 'month') {
    daterange.value.start_time = moment().startOf('month').format('YYYY-MM-DD')
    daterange.value.end_time = nowDate
  } else if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
  }
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
}

const dialogTitle = computed(() => {
  if (state.value === 'config') {
    return t('views.applicationOverview.ExportLogDialog.title')
  }
  return t('views.applicationOverview.ExportLogDialog.exportingTitle')
})

const dialogWidth = computed(() => {
  return state.value === 'config' ? '640px' : '480px'
})

const progress = ref(0)
const progressText = ref('')
const estimatedText = ref('')
const errorMessage = ref('')
let progressTimer: ReturnType<typeof setInterval> | null = null
let abortController: AbortController | null = null
let exportStartTime = 0

function simulateProgress() {
  progress.value = 0
  exportStartTime = Date.now()
  progressText.value = t('views.applicationOverview.ExportLogDialog.fetchingData', { percentage: '0' })
  estimatedText.value = ''

  progressTimer = setInterval(() => {
    const elapsed = (Date.now() - exportStartTime) / 1000
    let increment: number

    if (progress.value < 30) {
      increment = Math.random() * 8 + 5
      progressText.value = t('views.applicationOverview.ExportLogDialog.fetchingData', { percentage: Math.min(progress.value + increment, 30).toFixed(0) })
    } else if (progress.value < 80) {
      increment = Math.random() * 5 + 3
      progressText.value = t('views.applicationOverview.ExportLogDialog.fetchingData', { percentage: Math.min(progress.value + increment, 80).toFixed(0) })
    } else {
      increment = Math.random() * 2 + 1
      progressText.value = t('views.applicationOverview.ExportLogDialog.generatingFile', { percentage: Math.min(progress.value + increment, 90).toFixed(0) })
    }

    progress.value = Math.min(progress.value + increment, 90)

    const avgStepTime = elapsed / (progress.value / 5 + 1)
    const remainingSteps = (100 - progress.value) / 5
    const estimatedSeconds = Math.round(avgStepTime * remainingSteps)
    if (estimatedSeconds > 0) {
      estimatedText.value = t('views.applicationOverview.ExportLogDialog.estimatedRemaining', { seconds: estimatedSeconds })
    }
  }, 800)
}

function stopProgress() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

function completeProgress() {
  stopProgress()
  progress.value = 100
  progressText.value = t('views.applicationOverview.ExportLogDialog.generatingFile', { percentage: '100' })
  estimatedText.value = ''
  setTimeout(() => {
    closeDialog()
  }, 500)
}

async function startExport() {
  isExporting.value = true
  state.value = 'progress'
  simulateProgress()

  abortController = new AbortController()

  try {
    await loadSharedApi({ type: 'chatLog', systemType: props.apiType }).postExportChatLogCsv(
      props.id,
      { start_time: daterange.value.start_time, end_time: daterange.value.end_time },
      { fields: selectedFields.value },
    )
    completeProgress()
  } catch (err: any) {
    stopProgress()
    if (err?.message?.includes('canceled') || err?.code === 'ERR_CANCELED') {
      closeDialog()
      return
    }
    state.value = 'failed'
    const msg = err?.response?.data?.message || err?.message || t('views.applicationOverview.ExportLogDialog.exportFailed', { message: 'Unknown error' })
    errorMessage.value = t('views.applicationOverview.ExportLogDialog.exportFailed', { message: msg })
  } finally {
    isExporting.value = false
    abortController = null
  }
}

function cancelExport() {
  if (abortController) {
    abortController.abort()
  }
  stopProgress()
  closeDialog()
}

function retryExport() {
  state.value = 'config'
}

function resetToConfig() {
  state.value = 'config'
}

function closeDialog() {
  stopProgress()
  dialogVisible.value = false
}

function open() {
  state.value = 'config'
  historyDay.value = 7
  daterangeValue.value = ''
  daterange.value = { start_time: beforeDay(7), end_time: nowDate }
  selectedFields.value = [...defaultFieldKeys]
  progress.value = 0
  errorMessage.value = ''
  dialogVisible.value = true
}

function close() {
  closeDialog()
}

defineExpose({ open, close })
</script>

<style lang="scss" scoped>
.field-group-title {
  font-weight: 500;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.text-gray {
  color: var(--el-text-color-secondary);
}
.text-sm {
  font-size: 13px;
}
</style>
