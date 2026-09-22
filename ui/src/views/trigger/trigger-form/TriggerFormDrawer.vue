<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { TRIGGER_SCHEDULE_OPTIONS } from '@/constants/trigger'
import type { FormInstance, FormRules } from 'element-plus'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { RESOURCE_TYPE, TOOL_TYPE, TRIGGER_TYPE, TRIGGER_SCHEDULE_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerDetail, TriggerPayload, TriggerSetting, ResourceTriggerResource } from '@/api/types'
import TriggerTaskExecution from './task-execution/TriggerTaskExecution.vue'
import ToolTaskExecution from './task-execution/ToolTaskExecution.vue'
import ApplicationTaskExecution from './task-execution/ApplicationTaskExecution.vue'
import ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import RequestParameters from './request-parameters/RequestParametersTable.vue'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import { v4 as uuidv4 } from 'uuid'

const props = withDefaults(
  defineProps<{
    resource?: ResourceTriggerResource
    resourceApi?: typeof ResourceTriggerApi
    toolApi?: typeof ToolApi | typeof SystemToolApi
    toolWorkflowApi?: typeof WorkflowApi
  }>(),
  { resourceApi: () => ResourceTriggerApi, toolApi: () => ToolApi, toolWorkflowApi: () => WorkflowApi },
)
const emit = defineEmits<{ refresh: []; closed: [] }>()
/* 抽屉生命周期与详情 */
const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const detailFailed = ref(false)
const editingId = ref<string>()
const formRef = ref<FormInstance>()
const presetScheduleType = ref<TriggerSetting['schedule_type']>()
const taskExecutionRef = ref<{ validate: () => Promise<boolean | undefined>; reset?: () => void }>()
const resources = ref<Record<string, Partial<ApplicationDetail & ToolItem>>>({})

function createDefaultForm(): TriggerPayload {
  return {
    id: uuidv4(),
    name: '',
    desc: '',
    trigger_type: TRIGGER_TYPE.SCHEDULED,
    trigger_task: [],
    trigger_setting: {
      schedule_type: undefined,
      time: ['00:00'],
      days: [1],
      interval_unit: 'minutes',
      interval_value: 1,
      token: uuidv4().replaceAll('-', ''),
      body: [],
    },
  }
}
const form = ref<TriggerPayload>(createDefaultForm())
const eventUrl = computed(() => `${window.location.origin}${ADMIN_API_BASE_PATH}/trigger/v1/webhook/${form.value.id}`)

/** 工具触发任务需要完整的输入定义，工作流工具额外加载画布。 */
function loadToolResource(toolId: string) {
  return props.toolApi.getToolDetail(toolId).then((tool) => {
    if (tool.tool_type === TOOL_TYPE.WORKFLOW && !tool.work_flow)
      return props.toolWorkflowApi.getToolWorkflow(tool.id).then((workflow) => ({ ...tool, work_flow: workflow.work_flow }))
    return tool
  })
}

function fillDetail(detail: TriggerDetail) {
  const defaults = createDefaultForm()
  form.value = cloneDeep({
    id: detail.id,
    name: detail.name,
    desc: detail.desc ?? '',
    trigger_type: detail.trigger_type,
    is_active: detail.is_active,
    meta: detail.meta,
    trigger_task: detail.trigger_task,
    trigger_setting: {
      ...defaults.trigger_setting,
      ...detail.trigger_setting,
      days: detail.trigger_setting.days?.map(Number) ?? defaults.trigger_setting.days,
    },
  })
  detail.application_task_list?.forEach((application) => {
    if (application.id) resources.value[`${RESOURCE_TYPE.APPLICATION}:${application.id}`] = application
  })
  detail.tool_task_list?.forEach((tool) => {
    if (tool.id) resources.value[`${RESOURCE_TYPE.TOOL}:${tool.id}`] = tool
  })
}

function open(triggerId?: string) {
  resetData()
  editingId.value = triggerId
  visible.value = true
  const resource = props.resource
  if (!triggerId && !resource) return
  loading.value = true

  // 资源详情为单任务，统一转换成表单内部的任务数组。
  const detailRequest = triggerId
    ? resource
      ? props.resourceApi.getResourceTriggerDetail(resource, triggerId).then(
          (detail): TriggerDetail => ({
            ...detail,
            trigger_task: [detail.trigger_task],
            application_task_list: detail.application_task ? [detail.application_task] : [],
            tool_task_list: detail.tool_task ? [detail.tool_task] : [],
          }),
        )
      : TriggerApi.getTriggerDetail(triggerId)
    : Promise.resolve(undefined)

  return detailRequest
    .then((detail) => {
      if (!visible.value) return
      if (detail) fillDetail(detail)
      else if (resource) {
        form.value.trigger_task = [{ source_type: resource.source_type, source_id: resource.source_id, parameter: {} }]
      }
      // 补齐工具工作流参数；新建智能体任务时读取完整智能体详情。
      return Promise.all(
        form.value.trigger_task.map((task) => {
          const key = `${task.source_type}:${task.source_id}`
          if (task.source_type === RESOURCE_TYPE.TOOL)
            return loadToolResource(task.source_id).then((tool) => {
              resources.value[key] = tool
            })
          if (!resources.value[key])
            return ApplicationApi.getApplicationDetail(task.source_id).then((application) => {
              resources.value[key] = application
            })
          return Promise.resolve()
        }),
      )
    })
    .catch(() => {
      detailFailed.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

/* 触发周期及事件参数 */
const scheduleValue = computed<Array<number | string>>({
  get: () => {
    const setting = form.value.trigger_setting
    if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.INTERVAL) {
      return setting.interval_unit && setting.interval_value ? [TRIGGER_SCHEDULE_TYPE.INTERVAL, setting.interval_unit, setting.interval_value] : []
    }
    const time = setting.time?.[0]
    if (!time) return []
    if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.DAILY) return [TRIGGER_SCHEDULE_TYPE.DAILY, time]
    const day = setting.days?.[0]
    if (day === undefined) return []
    if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.WEEKLY) return [TRIGGER_SCHEDULE_TYPE.WEEKLY, Number(day), time]
    if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.MONTHLY) return [TRIGGER_SCHEDULE_TYPE.MONTHLY, String(day), time]
    return []
  },
  set: (value) => {
    const setting = form.value.trigger_setting
    if (!value?.length) {
      setting.schedule_type = undefined
      return
    }
    const [scheduleType, dayOrUnit, timeOrInterval] = value
    if (scheduleType === TRIGGER_SCHEDULE_TYPE.INTERVAL) {
      Object.assign(setting, { schedule_type: scheduleType, interval_unit: dayOrUnit, interval_value: timeOrInterval })
    } else if (scheduleType === TRIGGER_SCHEDULE_TYPE.WEEKLY || scheduleType === TRIGGER_SCHEDULE_TYPE.MONTHLY) {
      Object.assign(setting, { schedule_type: scheduleType, days: [dayOrUnit], time: [timeOrInterval] })
    } else {
      Object.assign(setting, { schedule_type: TRIGGER_SCHEDULE_TYPE.DAILY, time: [dayOrUnit] })
    }
  },
})
function handleSwitchScheduleMode() {
  const setting = form.value.trigger_setting
  if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.CRON) setting.schedule_type = presetScheduleType.value
  else {
    presetScheduleType.value = setting.schedule_type
    setting.schedule_type = TRIGGER_SCHEDULE_TYPE.CRON
  }
  formRef.value?.clearValidate('trigger_setting')
}

const triggerTypeOptions = [
  { value: TRIGGER_TYPE.SCHEDULED, label: '定时触发', description: '到设定时间后执行任务' },
  { value: TRIGGER_TYPE.EVENT, label: '事件触发', description: '当某个事件发生时执行任务' },
]
function handleSelectTriggerType(type: TriggerPayload['trigger_type']) {
  if (saving.value || loading.value) return
  form.value.trigger_type = type
  formRef.value?.clearValidate('trigger_setting')
}
function handleRefreshToken() {
  form.value.trigger_setting.token = uuidv4().replaceAll('-', '')
}

const rules: FormRules<TriggerPayload> = {
  name: [{ required: true, whitespace: true, message: '请输入触发器名称', trigger: 'blur' }],
  trigger_task: [{ type: 'array', required: true, min: 1, message: '请至少选择一个执行任务', trigger: 'change' }],
  trigger_setting: [
    {
      validator: (_rule, _value, callback) => {
        const setting = form.value.trigger_setting
        let error = ''
        if (form.value.trigger_type === TRIGGER_TYPE.EVENT) {
          const body = setting.body ?? []
          if (!setting.token?.trim()) error = '请生成 Bearer Token'
          else if (body.some(({ field }) => !field.trim())) error = '请填写请求参数名称'
          else if (new Set(body.map(({ field }) => field.trim())).size !== body.length) error = '请求参数名称不能重复'
        } else if (!setting.schedule_type) {
          error = '请选择触发周期'
        } else if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.CRON) {
          if (setting.cron_expression?.trim().split(/\s+/).length !== 5) error = '请输入有效的Cron 表达式'
        } else if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.INTERVAL) {
          if (!Number.isInteger(setting.interval_value) || (setting.interval_value ?? 0) < 1) error = '请选择触发周期'
        } else {
          if (!setting.time?.length || setting.time.some((time) => !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) error = '请选择触发周期'
          if ([TRIGGER_SCHEDULE_TYPE.WEEKLY, TRIGGER_SCHEDULE_TYPE.MONTHLY].some((type) => type === setting.schedule_type) && !setting.days?.length)
            error = '请选择触发周期'
        }
        callback(error ? new Error(error) : undefined)
      },
      trigger: 'change',
    },
  ],
}

/* 表单校验及保存 */
function handleSave() {
  if (saving.value || loading.value || detailFailed.value) return
  form.value.name = form.value.name.trim()
  saving.value = true
  return nextTick()
    .then(() => Promise.all([formRef.value?.validate().catch(() => false), taskExecutionRef.value?.validate()]))
    .then((validations) => {
      if (validations.some((valid) => !valid)) {
        return
      }
      const payload = cloneDeep(form.value)
      const setting = payload.trigger_setting
      // 按当前触发方式提交配置；切换编辑模式时仍保留草稿。
      let activeSetting: TriggerSetting
      if (payload.trigger_type === TRIGGER_TYPE.EVENT)
        activeSetting = { token: setting.token, body: setting.body?.map((field) => ({ ...field, field: field.field.trim() })) }
      else if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.CRON)
        activeSetting = { schedule_type: TRIGGER_SCHEDULE_TYPE.CRON, cron_expression: setting.cron_expression?.trim() }
      else if (setting.schedule_type === TRIGGER_SCHEDULE_TYPE.INTERVAL)
        activeSetting = {
          schedule_type: TRIGGER_SCHEDULE_TYPE.INTERVAL,
          interval_unit: setting.interval_unit,
          interval_value: setting.interval_value,
        }
      else
        activeSetting = {
          schedule_type: setting.schedule_type,
          time: setting.time,
          ...(setting.schedule_type === TRIGGER_SCHEDULE_TYPE.DAILY ? {} : { days: setting.days }),
        }
      payload.trigger_setting = activeSetting
      const resource = props.resource
      const request = resource
        ? editingId.value
          ? props.resourceApi.putResourceTrigger(resource, editingId.value, payload)
          : props.resourceApi.postResourceTrigger(resource, payload)
        : editingId.value
          ? TriggerApi.putTrigger(editingId.value, payload)
          : TriggerApi.postTrigger(payload)
      return request.then(() => {
        MsgSuccess(editingId.value ? '保存成功' : '创建成功')
        visible.value = false
        emit('refresh')
      })
    })
    .finally(() => {
      saving.value = false
    })
}

function resetData() {
  form.value = createDefaultForm()
  editingId.value = undefined
  loading.value = false
  saving.value = false
  detailFailed.value = false
  resources.value = {}
  taskExecutionRef.value?.reset?.()
  presetScheduleType.value = undefined
  formRef.value?.clearValidate()
}

function handleBeforeClose(done: () => void) {
  if (!saving.value) done()
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="editingId ? '编辑触发器' : '创建触发器'" @closed="handleClosed" :before-close="handleBeforeClose">
    <div v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="触发器名称" prop="name"
          ><el-input v-model="form.name" maxlength="64" show-word-limit placeholder="请输入触发器名称"
        /></el-form-item>
        <el-form-item label="描述" prop="desc"
          ><el-input v-model="form.desc" type="textarea" :rows="3" maxlength="200" show-word-limit placeholder="请输入"
        /></el-form-item>
        <el-form-item label="类型" required>
          <div class="w-full space-y-2">
            <MkSourceCard
              v-for="option in triggerTypeOptions"
              :key="option.value"
              :title="option.label"
              class="min-h-0!"
              :class="{ 'border-primary!': form.trigger_type === option.value }"
              :aria-checked="form.trigger_type === option.value"
              @click="handleSelectTriggerType(option.value)"
            >
              <template #icon>
                <TriggerIcon :type="option.value" :size="24" />
              </template>
              <template #subtitle>{{ option.description }}</template>
              <template v-if="form.trigger_type === option.value" #default>
                <el-form-item prop="trigger_setting" class="mb-0!" @click.stop @keydown.stop>
                  <div class="mk-gray-card-lg w-full text-N900">
                    <!-- 定时触发 -->
                    <template v-if="option.value === TRIGGER_TYPE.SCHEDULED">
                      <div class="flex-between mb-2">
                        <span class="mk-required">{{
                          form.trigger_setting.schedule_type === TRIGGER_SCHEDULE_TYPE.CRON ? 'Cron 表达式' : '触发周期'
                        }}</span>
                        <!-- 切换周期设置与 Cron 表达式 -->
                        <MkTooltip
                          :content="form.trigger_setting.schedule_type === TRIGGER_SCHEDULE_TYPE.CRON ? '切换为周期设置' : '切换为 Cron 表达式'"
                          placement="top"
                        >
                          <el-button text type="primary" @click="handleSwitchScheduleMode">
                            <MkIcon name="icon_swich" />
                          </el-button>
                        </MkTooltip>
                      </div>
                      <el-cascader
                        v-if="form.trigger_setting.schedule_type !== TRIGGER_SCHEDULE_TYPE.CRON"
                        v-model="scheduleValue"
                        :options="TRIGGER_SCHEDULE_OPTIONS"
                        :teleported="false"
                        class="w-full"
                        clearable
                        placeholder="请选择触发周期"
                      />
                      <el-input v-else v-model="form.trigger_setting.cron_expression" placeholder="请输入Cron表达式（如：0 0 1 * *）" />
                    </template>
                    <!-- 事件触发 -->
                    <template v-else>
                      <p class="mb-2">事件 URL</p>
                      <el-input v-model="eventUrl" readonly>
                        <template #suffix>
                          <el-button text @click="copyText(eventUrl)" class="-mr-1">
                            <MkIcon name="icon_copy_outlined" class="text-N600" />
                          </el-button>
                        </template>
                      </el-input>

                      <p class="mb-2 mt-3">Bearer Token</p>

                      <el-input v-model="form.trigger_setting.token" readonly>
                        <template #suffix>
                          <el-button text @click="copyText(form.trigger_setting.token)">
                            <MkIcon name="icon_copy_outlined" class="text-N600" />
                          </el-button>
                          <!-- 刷新Token -->
                          <el-button text @click="handleRefreshToken" class="-mr-1">
                            <MkIcon name="icon_refresh_outlined" class="text-N600" />
                          </el-button>
                        </template>
                      </el-input>
                      <!-- TODO 请求参数 -->
                      <RequestParameters v-model="form.trigger_setting.body" />
                    </template>
                  </div>
                </el-form-item>
              </template>
            </MkSourceCard>
          </div>
        </el-form-item>
        <!-- 任务执行 -->
        <el-form-item label="任务执行" prop="trigger_task">
          <div class="mk-gray-card-lg w-full">
            <TriggerTaskExecution
              v-if="!resource"
              ref="taskExecutionRef"
              v-model="form.trigger_task"
              :initial-resources="resources"
              v-model:loading="loading"
              :trigger-type="form.trigger_type"
              :body="form.trigger_setting.body ?? []"
              :disabled="saving || loading"
              @change="formRef?.clearValidate('trigger_task')"
            />
            <ToolTaskExecution
              v-else-if="resource.source_type === RESOURCE_TYPE.TOOL && !loading && !detailFailed"
              ref="taskExecutionRef"
              v-model="form.trigger_task"
              :tool="resources[`${resource.source_type}:${resource.source_id}`]"
              :trigger-type="form.trigger_type"
              :body="form.trigger_setting.body ?? []"
              :disabled="saving || loading"
            />
            <ApplicationTaskExecution
              v-else-if="resource.source_type === RESOURCE_TYPE.APPLICATION && !loading && !detailFailed"
              ref="taskExecutionRef"
              v-model="form.trigger_task"
              :application="resources[`${resource.source_type}:${resource.source_id}`]"
              :trigger-type="form.trigger_type"
              :body="form.trigger_setting.body ?? []"
              :disabled="saving || loading"
            />
          </div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消触发器编辑 -->
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 保存触发器配置 -->
      <el-button type="primary" :loading="saving" :disabled="loading || detailFailed" @click="handleSave">{{
        editingId ? '保存' : '创建'
      }}</el-button>
    </template>
  </MkDrawer>
</template>
