<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { RESOURCE_TYPE, TOOL_TYPE, STATE_TYPES } from '@/api/enums'
import type { TriggerTaskRecord, TriggerTaskRecordDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { WorkflowMode } from '@/workflow-canvas/types'

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
const nodeDetails = computed<ExecutionNodeDetail[]>(() => Object.values((isTool.value ? detail.value?.meta?.details : detail.value?.details) ?? {}))

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
        <!-- 返回输入参数 -->
        <el-button class="mr-1" text @click="visible = false">
          <MkIcon name="icon_arrow-left_outlined" :size="20" />
        </el-button>
        <h4>执行详情</h4>
      </div>
    </template>
    <div v-loading="loading">
      <!-- 执行记录 -->
      <h4 class="mk-title-decoration mb-4">执行记录</h4>
      <el-card shadow="never">
        <div class="grid grid-cols-4 gap-4">
          <div class="min-w-0">
            <p class="mb-1 text-N600">触发任务</p>
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
            <p class="mb-1 text-N600">状态</p>
            <MkStatusLabel :status="record.state" />
          </div>
          <div>
            <p class="mb-1 text-N600">耗时</p>
            {{ runTime == null ? '-' : `${runTime.toFixed(2)} s` }}
          </div>
          <div>
            <p class="mb-1 text-N600">执行时间</p>
            {{ datetimeFormat(record.create_time) }}
          </div>
        </div>
      </el-card>
      <!-- 执行详情 -->
      <h4 class="mk-title-decoration my-4">执行详情</h4>

      <template v-if="triggerFailed">
        <div class="mk-gray-card-sm mb-2">
          <h6 class="mb-2">触发器入参</h6>
          <div>
            {{ detail?.meta?.input }}
          </div>
        </div>
        <div class="mk-gray-card-sm">
          <h6 class="mb-2">错误信息</h6>
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
      <!-- 浏览上一条执行记录 -->
      <el-button plain :disabled="previousDisabled || loading" @click="emit('previous')">上一条</el-button>
      <!-- 浏览下一条执行记录 -->
      <el-button plain :disabled="nextDisabled || loading" @click="emit('next')">下一条</el-button>
    </template>
  </MkDrawer>
</template>
