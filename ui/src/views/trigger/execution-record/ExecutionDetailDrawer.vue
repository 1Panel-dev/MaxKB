<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TriggerTaskRecord, TriggerTaskRecordDetail } from '@/api/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { RESOURCE_TYPE, STATE_TYPES, TOOL_TYPE } from '@/api/enums'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import { EXECUTION_STATUS_OPTIONS } from '@/constants/state'
import { datetimeFormat } from '@/utils/time'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  record: TriggerTaskRecord
  previousDisabled: boolean
  nextDisabled: boolean
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ previous: []; next: [] }>()

/* 当前任务的执行结果 */
const loading = ref(false)
const detail = ref<TriggerTaskRecordDetail>()
const isTool = computed(() => props.record.source_type === RESOURCE_TYPE.TOOL)
const triggerFailed = computed(() => detail.value?.state === STATE_TYPES.TRIGGER_ERROR)
const runTime = computed(() => detail.value?.run_time ?? props.record.run_time)
const nodeDetails = computed<ExecutionNodeDetail[]>(() => {
  const executionDetails = Object.fromEntries(Object.entries(detail.value?.details ?? {}))
  if (isTool.value && executionDetails.tool_call) {
    executionDetails.tool_call = {
      ...executionDetails.tool_call,
      name: executionDetails.tool_call.name || props.record.source_name || t('tool.title'),
    }
  }
  return Object.values(executionDetails)
})

function loadDetail() {
  loading.value = true
  detail.value = undefined
  return TriggerApi.getTriggerTaskRecordDetails(props.record.trigger_id, props.record.trigger_task_id, props.record.id)
    .then((result) => {
      detail.value = result
    })
    .finally(() => {
      loading.value = false
    })
}
watch(
  [() => props.record.id, visible],
  ([, opened]) => {
    if (opened) void loadDetail()
  },
  { immediate: true },
)
</script>

<template>
  <MkDrawer v-model="visible" size="840" :modal="false">
    <template #header>
      <div class="-ml-2 flex-align-center">
        <!-- 返回执行记录 -->
        <el-button class="mr-1" text @click="visible = false">
          <MkIcon name="icon_arrow-left_outlined" :size="20" />
        </el-button>
        <h4>{{ t('resource.executionRecords.detailTitle') }}</h4>
      </div>
    </template>
    <div v-loading="loading">
      <!-- 执行记录 -->
      <h4 class="mk-title-decoration mb-4">{{ t('resource.executionRecords.title') }}</h4>
      <el-card shadow="never">
        <div class="grid grid-cols-4 gap-4">
          <div class="min-w-0">
            <p class="mb-1 text-N600">{{ t('trigger.executionRecords.task') }}</p>
            <div class="flex-align-center gap-2">
              <ToolIcon
                v-if="isTool"
                :icon="record.source_icon ?? undefined"
                :type="record.type === TOOL_TYPE.WORKFLOW ? TOOL_TYPE.WORKFLOW : TOOL_TYPE.CUSTOM"
                :size="20"
              />
              <ApplicationIcon v-else :icon="record.source_icon ?? undefined" :size="20" />
              <span class="min-w-0 flex-1 truncate" :title="record.source_name ?? undefined">{{ record.source_name }}</span>
            </div>
          </div>
          <div>
            <p class="mb-1 text-N600">{{ t('common.status.label') }}</p>
            <MkStatusLabel
              v-if="EXECUTION_STATUS_OPTIONS[detail?.state ?? record.state]"
              :type="EXECUTION_STATUS_OPTIONS[detail?.state ?? record.state].type"
              :label="t(EXECUTION_STATUS_OPTIONS[detail?.state ?? record.state].labelKey)"
              :icon="EXECUTION_STATUS_OPTIONS[detail?.state ?? record.state].icon"
            />
            <span v-else>{{ detail?.state ?? record.state }}</span>
          </div>
          <div>
            <p class="mb-1 text-N600">{{ t('common.labels.duration') }}</p>
            {{ runTime == null ? '-' : `${runTime.toFixed(2)} s` }}
          </div>
          <div>
            <p class="mb-1 text-N600">{{ t('resource.executionRecords.executionTime') }}</p>
            {{ datetimeFormat(record.create_time) }}
          </div>
        </div>
      </el-card>
      <!-- 执行详情 -->
      <h4 class="mk-title-decoration my-4">{{ t('resource.executionRecords.detailTitle') }}</h4>

      <template v-if="triggerFailed">
        <div class="mk-gray-card-sm mb-2">
          <h6 class="mb-2">{{ t('trigger.executionRecords.input') }}</h6>
          <div>
            {{ detail?.meta?.input }}
          </div>
        </div>
        <div class="mk-gray-card-sm">
          <h6 class="mb-2">{{ t('resource.executionRecords.errorMessage') }}</h6>
          <div>
            {{ detail?.meta?.err_message }}
          </div>
        </div>
      </template>
      <ExecutionDetailContent
        v-if="!triggerFailed && nodeDetails.length"
        :detail="nodeDetails"
        :workflow-mode="isTool ? WorkflowMode.Tool : WorkflowMode.Application"
      />
    </div>
    <template #footer>
      <!-- 浏览上一个执行记录 -->
      <el-button plain :disabled="previousDisabled || loading" @click="emit('previous')">{{ t('common.actions.previousItem') }}</el-button>
      <!-- 浏览下一个执行记录 -->
      <el-button plain :disabled="nextDisabled || loading" @click="emit('next')">{{ t('common.actions.nextItem') }}</el-button>
    </template>
  </MkDrawer>
</template>
