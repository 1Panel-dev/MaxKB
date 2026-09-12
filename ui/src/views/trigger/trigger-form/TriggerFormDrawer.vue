<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { TRIGGER_SCHEDULE_OPTIONS } from '@/constants/trigger'
import type { FormInstance, FormRules } from 'element-plus'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { RESOURCE_TYPE, TRIGGER_TYPE, TRIGGER_SCHEDULE_TYPE as SCHEDULE, TRIGGER_INTERVAL_UNIT as INTERVAL } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerPayload, TriggerSetting } from '@/api/types'
import TaskExecution from './task-execution/TaskExecution.vue'
import RequestParameters from './request-parameters/RequestParameters.vue'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{ refresh: [] }>()
/* 抽屉生命周期与详情 */
const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const detailFailed = ref(false)
const editingId = ref<string>()
const formRef = ref<FormInstance>()
const presetScheduleType = ref<TriggerSetting['schedule_type']>()
const taskExecutionRef = ref<InstanceType<typeof TaskExecution>>()
const resources = ref<Record<string, Partial<ApplicationDetail & ToolItem>>>({})

// HTTP 部署中 randomUUID 可能不可用，使用浏览器安全随机数生成 UUID。
function createTriggerUuid() {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  bytes[6] = (bytes[6]! & 0x0f) | 0x40
  bytes[8] = (bytes[8]! & 0x3f) | 0x80
  const hex = Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('')
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

function createDefaultForm(): TriggerPayload {
  return {
    id: createTriggerUuid(),
    name: '',
    desc: '',
    trigger_type: TRIGGER_TYPE.SCHEDULED,
    trigger_task: [],
    trigger_setting: {
      schedule_type: undefined,
      time: ['00:00'],
      days: [1],
      interval_unit: INTERVAL.MINUTES,
      interval_value: 1,
      token: createTriggerUuid().replaceAll('-', ''),
      body: [],
    },
  }
}
const form = ref<TriggerPayload>(createDefaultForm())
const eventUrl = computed(() => `${window.location.origin}${ADMIN_API_BASE_PATH}/trigger/v1/webhook/${form.value.id}`)

function open(triggerId?: string) {
  resetData()
  editingId.value = triggerId
  visible.value = true
  if (!triggerId) return
  loading.value = true
  return TriggerApi.getTriggerDetail(triggerId)
    .then((detail) => {
      if (!visible.value) return
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
    if (setting.schedule_type === SCHEDULE.INTERVAL) {
      return setting.interval_unit && setting.interval_value ? [SCHEDULE.INTERVAL, setting.interval_unit, setting.interval_value] : []
    }
    const time = setting.time?.[0]
    if (!time) return []
    if (setting.schedule_type === SCHEDULE.DAILY) return [SCHEDULE.DAILY, time]
    const day = setting.days?.[0]
    if (day === undefined) return []
    if (setting.schedule_type === SCHEDULE.WEEKLY) return [SCHEDULE.WEEKLY, Number(day), time]
    if (setting.schedule_type === SCHEDULE.MONTHLY) return [SCHEDULE.MONTHLY, String(day), time]
    return []
  },
  set: (value) => {
    const setting = form.value.trigger_setting
    if (!value?.length) {
      setting.schedule_type = undefined
      return
    }
    const [scheduleType, dayOrUnit, timeOrInterval] = value
    if (scheduleType === SCHEDULE.INTERVAL) {
      Object.assign(setting, { schedule_type: scheduleType, interval_unit: dayOrUnit, interval_value: timeOrInterval })
    } else if (scheduleType === SCHEDULE.WEEKLY || scheduleType === SCHEDULE.MONTHLY) {
      Object.assign(setting, { schedule_type: scheduleType, days: [dayOrUnit], time: [timeOrInterval] })
    } else {
      Object.assign(setting, { schedule_type: SCHEDULE.DAILY, time: [dayOrUnit] })
    }
  },
})
function handleSwitchScheduleMode() {
  const setting = form.value.trigger_setting
  if (setting.schedule_type === SCHEDULE.CRON) setting.schedule_type = presetScheduleType.value
  else {
    presetScheduleType.value = setting.schedule_type
    setting.schedule_type = SCHEDULE.CRON
  }
  formRef.value?.clearValidate('trigger_setting')
}

const triggerTypeOptions = [
  { value: TRIGGER_TYPE.SCHEDULED, label: '定时触发', description: '到设定时间后，自动提炼周期内所有对话，生成记忆' },
  { value: TRIGGER_TYPE.EVENT, label: '事件触发', description: '当某个事件发生时执行任务' },
]
function handleSelectTriggerType(type: TriggerPayload['trigger_type']) {
  if (saving.value || loading.value) return
  form.value.trigger_type = type
  formRef.value?.clearValidate('trigger_setting')
}
function handleRefreshToken() {
  form.value.trigger_setting.token = createTriggerUuid().replaceAll('-', '')
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
        } else if (setting.schedule_type === SCHEDULE.CRON) {
          if (setting.cron_expression?.trim().split(/\s+/).length !== 5) error = '请输入有效的Cron 表达式'
        } else if (setting.schedule_type === SCHEDULE.INTERVAL) {
          if (!Number.isInteger(setting.interval_value) || (setting.interval_value ?? 0) < 1) error = '请选择触发周期'
        } else {
          if (!setting.time?.length || setting.time.some((time) => !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) error = '请选择触发周期'
          if ([SCHEDULE.WEEKLY, SCHEDULE.MONTHLY].some((type) => type === setting.schedule_type) && !setting.days?.length) error = '请选择触发周期'
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
      else if (setting.schedule_type === SCHEDULE.CRON)
        activeSetting = { schedule_type: SCHEDULE.CRON, cron_expression: setting.cron_expression?.trim() }
      else if (setting.schedule_type === SCHEDULE.INTERVAL)
        activeSetting = { schedule_type: SCHEDULE.INTERVAL, interval_unit: setting.interval_unit, interval_value: setting.interval_value }
      else
        activeSetting = {
          schedule_type: setting.schedule_type,
          time: setting.time,
          ...(setting.schedule_type === SCHEDULE.DAILY ? {} : { days: setting.days }),
        }
      payload.trigger_setting = activeSetting
      const request = editingId.value ? TriggerApi.putTrigger(editingId.value, payload) : TriggerApi.postTrigger(payload)
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
  taskExecutionRef.value?.reset()
  presetScheduleType.value = undefined
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="editingId ? '编辑触发器' : '创建触发器'" @closed="resetData">
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
                  <div class="mk-gray-card w-full p-4! rounded-xl! text-N900">
                    <!-- 定时触发 -->
                    <template v-if="option.value === TRIGGER_TYPE.SCHEDULED">
                      <div class="flex-between mb-2">
                        <span class="mk-required">{{ form.trigger_setting.schedule_type === SCHEDULE.CRON ? 'Cron 表达式' : '触发周期' }}</span>
                        <!-- 切换周期设置与 Cron 表达式 -->
                        <el-tooltip
                          :content="form.trigger_setting.schedule_type === SCHEDULE.CRON ? '切换为周期设置' : '切换为 Cron 表达式'"
                          placement="top"
                        >
                          <el-button text type="primary" @click="handleSwitchScheduleMode">
                            <MkIcon name="icon_swich" />
                          </el-button>
                        </el-tooltip>
                      </div>
                      <el-cascader
                        v-if="form.trigger_setting.schedule_type !== SCHEDULE.CRON"
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
                      <!-- 请求参数 -->
                      <!-- <RequestParameters v-model="form.trigger_setting.body" /> -->
                    </template>
                  </div>
                </el-form-item>
              </template>
            </MkSourceCard>
          </div>
        </el-form-item>
        <!-- 任务执行 -->
        <el-form-item label="任务执行" prop="trigger_task">
          <div class="mk-gray-card w-full p-4! rounded-xl!">
            <TaskExecution
              ref="taskExecutionRef"
              v-model="form.trigger_task"
              :initial-resources="resources"
              v-model:loading="loading"
              :trigger-type="form.trigger_type"
              :body="form.trigger_setting.body ?? []"
              :disabled="saving || loading"
              @change="formRef?.clearValidate('trigger_task')"
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
