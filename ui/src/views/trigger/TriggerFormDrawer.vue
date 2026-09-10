<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import ApplicationApi from '@/api/admin/workspace/application/application'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import {
  RESOURCE_TYPE,
  TOOL_TYPE,
  TRIGGER_TYPE,
  TRIGGER_SCHEDULE_TYPE as SCHEDULE,
  TRIGGER_INTERVAL_UNIT as INTERVAL,
  TRIGGER_BODY_TYPE,
} from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerPayload, TriggerSetting, TriggerTaskPayload, TriggerTaskSource } from '@/api/types'
import SelectApplicationDialog from '@/components/business/select-application-dialog/index.vue'
import SelectToolDialog from '@/components/business/select-tool-dialog/index.vue'
import TaskParameters from './components/TaskParameters.vue'
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
const expandedTaskKeys = ref<string[]>([])
const parameterRefs = ref<InstanceType<typeof TaskParameters>[]>([])
const applicationDialogRef = ref<InstanceType<typeof SelectApplicationDialog>>()
const toolDialogRef = ref<InstanceType<typeof SelectToolDialog>>()
const resources = ref<Record<string, Partial<ApplicationDetail & ToolItem>>>({})
let requestVersion = 0

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
      schedule_type: SCHEDULE.DAILY,
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
const taskKey = (task: Pick<TriggerTaskPayload, 'source_type' | 'source_id'>) => `${task.source_type}:${task.source_id}`

function resetData() {
  requestVersion++
  form.value = createDefaultForm()
  editingId.value = undefined
  loading.value = false
  saving.value = false
  detailFailed.value = false
  resources.value = {}
  expandedTaskKeys.value = []
  formRef.value?.clearValidate()
}

function open(triggerId?: string) {
  resetData()
  editingId.value = triggerId
  visible.value = true
  if (!triggerId) return
  const version = requestVersion
  loading.value = true
  return TriggerApi.getTriggerDetail(triggerId)
    .then((detail) => {
      if (version !== requestVersion || !visible.value) return
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
      if (version === requestVersion) detailFailed.value = true
    })
    .finally(() => {
      if (version === requestVersion) loading.value = false
    })
}

/* 触发周期及事件参数 */
const scheduleOptions = [
  { label: '每天', value: SCHEDULE.DAILY },
  { label: '每周', value: SCHEDULE.WEEKLY },
  { label: '每月', value: SCHEDULE.MONTHLY },
  { label: '时间间隔', value: SCHEDULE.INTERVAL },
  { label: 'Cron 表达式', value: SCHEDULE.CRON },
]
const dayOptions = computed(() =>
  Array.from({ length: form.value.trigger_setting.schedule_type === SCHEDULE.WEEKLY ? 7 : 31 }, (_, index) => ({
    value: index + 1,
    label:
      form.value.trigger_setting.schedule_type === SCHEDULE.WEEKLY ? `星期${['一', '二', '三', '四', '五', '六', '日'][index]}` : `${index + 1}日`,
  })),
)
function handleScheduleChange() {
  form.value.trigger_setting.days = [1]
  form.value.trigger_setting.time ||= ['00:00']
  form.value.trigger_setting.interval_unit ||= INTERVAL.MINUTES
  form.value.trigger_setting.interval_value ||= 1
  formRef.value?.clearValidate('trigger_setting')
}
function handleAddBodyField() {
  ;(form.value.trigger_setting.body ||= []).push({ field: '', type: TRIGGER_BODY_TYPE.STRING, desc: '', required: false })
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
        } else if (setting.schedule_type === SCHEDULE.CRON) {
          if (setting.cron_expression?.trim().split(/\s+/).length !== 5) error = '请输入五段 Cron 表达式：分 时 日 月 周'
        } else if (setting.schedule_type === SCHEDULE.INTERVAL) {
          if (!Number.isInteger(setting.interval_value) || (setting.interval_value ?? 0) < 1) error = '时间间隔必须为正整数'
        } else {
          if (!setting.time?.length || setting.time.some((time) => !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) error = '请选择执行时间'
          if ([SCHEDULE.WEEKLY, SCHEDULE.MONTHLY].some((type) => type === setting.schedule_type) && !setting.days?.length) error = '请选择执行日期'
        }
        callback(error ? new Error(error) : undefined)
      },
      trigger: 'change',
    },
  ],
}

/* 选择执行资源并保留已有任务参数 */
function handleOpenApplicationDialog() {
  applicationDialogRef.value?.open(
    form.value.trigger_task
      .filter((task) => task.source_type === RESOURCE_TYPE.APPLICATION)
      .map((task) => ({ ...resources.value[taskKey(task)], id: task.source_id })),
  )
}
function handleOpenToolDialog() {
  toolDialogRef.value?.open(
    form.value.trigger_task
      .filter((task) => task.source_type === RESOURCE_TYPE.TOOL)
      .map((task) => ({ ...resources.value[taskKey(task)], id: task.source_id })),
  )
}
function handleSelectResources(source: TriggerTaskSource, selected: { id: string }[]) {
  const version = requestVersion
  const existingTasks = new Map(form.value.trigger_task.filter((task) => task.source_type === source).map((task) => [task.source_id, task]))
  loading.value = true
  // 先完整加载新增资源，任一请求失败时保留原来的关联任务。
  return Promise.all(
    selected.map((resource) => {
      const key = `${source}:${resource.id}`
      if (resources.value[key]) return Promise.resolve({ id: resource.id, resource: resources.value[key]! })
      if (source === RESOURCE_TYPE.APPLICATION)
        return ApplicationApi.getApplicationDetail(resource.id).then((application) => ({ id: resource.id, resource: application }))
      return ToolApi.getToolDetail(resource.id).then((tool) => {
        if (tool.tool_type === TOOL_TYPE.WORKFLOW && !tool.work_flow)
          return WorkflowApi.getToolWorkflow(tool.id).then((workflow) => ({ id: tool.id, resource: { ...tool, work_flow: workflow.work_flow } }))
        return { id: tool.id, resource: tool }
      })
    }),
  )
    .then((selectedResources) => {
      if (version !== requestVersion || !visible.value) return
      selectedResources.forEach(({ id, resource }) => {
        resources.value[`${source}:${id}`] = resource
      })
      form.value.trigger_task = [
        ...form.value.trigger_task.filter((task) => task.source_type !== source),
        ...selectedResources.map(({ id }) => existingTasks.get(id) ?? { source_type: source, source_id: id, parameter: {} }),
      ]
      expandedTaskKeys.value = form.value.trigger_task.map(taskKey)
      formRef.value?.clearValidate('trigger_task')
    })
    .finally(() => {
      if (version === requestVersion) loading.value = false
    })
}
function handleRemoveTask(task: TriggerTaskPayload) {
  form.value.trigger_task = form.value.trigger_task.filter((current) => current !== task)
}

/* 表单校验及保存 */
function handleSave() {
  if (saving.value || loading.value || detailFailed.value || !canSave.value) return
  form.value.name = form.value.name.trim()
  saving.value = true
  return nextTick()
    .then(() =>
      Promise.all([formRef.value?.validate().catch(() => false), ...parameterRefs.value.map((parameter) => parameter.validate().catch(() => false))]),
    )
    .then((validations) => {
      if (validations.some((valid) => !valid)) {
        expandedTaskKeys.value = form.value.trigger_task.map(taskKey)
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
defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    :title="editingId ? '编辑触发器' : '新建触发器'"
    size="720"
    :before-close="
      (done: () => void) => {
        if (!saving) done()
      }
    "
    @closed="resetData"
  >
    <div v-loading="loading">
      <el-alert v-if="detailFailed" title="触发器详情加载失败，请关闭后重试" type="error" :closable="false" />
      <el-form v-else ref="formRef" :model="form" :rules="rules" label-position="top" :disabled="saving || loading || !canSave" @submit.prevent>
        <el-form-item label="触发器名称" prop="name"
          ><el-input v-model="form.name" maxlength="64" show-word-limit placeholder="请输入触发器名称"
        /></el-form-item>
        <el-form-item label="描述" prop="desc"
          ><el-input v-model="form.desc" type="textarea" :rows="3" maxlength="256" show-word-limit
        /></el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.trigger_type">
            <el-radio-button :value="TRIGGER_TYPE.SCHEDULED">定时触发</el-radio-button>
            <el-radio-button :value="TRIGGER_TYPE.EVENT">事件触发</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item prop="trigger_setting">
          <div class="mk-gray-card w-full">
            <template v-if="form.trigger_type === TRIGGER_TYPE.SCHEDULED">
              <p class="mb-2">触发周期</p>
              <el-select v-model="form.trigger_setting.schedule_type" @change="handleScheduleChange"
                ><el-option v-for="option in scheduleOptions" :key="option.value" v-bind="option"
              /></el-select>
              <template v-if="form.trigger_setting.schedule_type === SCHEDULE.CRON">
                <el-input v-model="form.trigger_setting.cron_expression" class="mt-3" placeholder="例如：0 9 * * *" />
                <p class="mt-1 text-sm text-N600">分 时 日 月 周，使用服务器时区；每周从周一（0）开始。</p>
              </template>
              <div v-else-if="form.trigger_setting.schedule_type === SCHEDULE.INTERVAL" class="mt-3 flex gap-2">
                <el-input-number v-model="form.trigger_setting.interval_value" :min="1" :precision="0" controls-position="right" align="left" />
                <el-select v-model="form.trigger_setting.interval_unit"
                  ><el-option label="分钟" :value="INTERVAL.MINUTES" /><el-option label="小时" :value="INTERVAL.HOURS"
                /></el-select>
              </div>
              <template v-else>
                <el-select
                  v-if="form.trigger_setting.schedule_type !== SCHEDULE.DAILY"
                  v-model="form.trigger_setting.days"
                  multiple
                  class="mt-3"
                  placeholder="请选择执行日期"
                  ><el-option v-for="option in dayOptions" :key="option.value" v-bind="option"
                /></el-select>
                <div v-for="(_time, index) in form.trigger_setting.time" :key="index" class="mt-3 flex items-center gap-2">
                  <el-time-picker
                    v-model="form.trigger_setting.time![index]"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="请选择执行时间"
                    :clearable="false"
                  />
                  <!-- 移除执行时间 -->
                  <el-button :disabled="form.trigger_setting.time!.length <= 1" text @click="form.trigger_setting.time!.splice(index, 1)"
                    >删除</el-button
                  >
                </div>
                <!-- 添加执行时间 -->
                <el-button link type="primary" class="mt-3" @click="form.trigger_setting.time!.push('00:00')">添加执行时间</el-button>
              </template>
            </template>
            <template v-else>
              <p class="mb-2">事件 URL</p>
              <div class="flex gap-2">
                <el-input :model-value="eventUrl" readonly /><!-- 复制事件地址 --><el-button @click="copyText(eventUrl)">复制</el-button>
              </div>
              <p class="mb-2 mt-3">Bearer Token</p>
              <div class="flex gap-2">
                <el-input v-model="form.trigger_setting.token" readonly /><!-- 复制事件令牌 --><el-button
                  @click="copyText(form.trigger_setting.token)"
                  >复制</el-button
                ><!-- 重新生成事件令牌 --><el-button @click="handleRefreshToken">刷新</el-button>
              </div>
              <div class="flex-between mt-4 mb-2">
                <h6>请求参数</h6>
                <!-- 添加请求参数 --><el-button link type="primary" @click="handleAddBodyField">添加参数</el-button>
              </div>
              <div v-for="(field, index) in form.trigger_setting.body" :key="index" class="mb-2 flex items-center gap-2">
                <el-input v-model="field.field" placeholder="参数名" />
                <el-select v-model="field.type"><el-option v-for="type in TRIGGER_BODY_TYPE" :key="type" :label="type" :value="type" /></el-select>
                <el-input v-model="field.desc" placeholder="描述" />
                <el-checkbox v-model="field.required">必填</el-checkbox>
                <!-- 删除请求参数 -->
                <el-button text @click="form.trigger_setting.body!.splice(index, 1)">删除</el-button>
              </div>
            </template>
          </div>
        </el-form-item>
        <el-form-item label="执行任务" prop="trigger_task">
          <div class="w-full">
            <div class="mb-3 flex gap-2">
              <!-- 选择执行智能体 -->
              <el-button @click="handleOpenApplicationDialog">选择智能体</el-button>
              <!-- 选择执行工具 -->
              <el-button @click="handleOpenToolDialog">选择工具</el-button>
            </div>
            <el-collapse v-model="expandedTaskKeys">
              <el-collapse-item v-for="task in form.trigger_task" :key="taskKey(task)" :name="taskKey(task)">
                <template #title>
                  <span class="flex-1 truncate" :title="resources[taskKey(task)]?.name || task.source_id"
                    >{{ task.source_type === RESOURCE_TYPE.APPLICATION ? '智能体' : '工具' }}：{{
                      resources[taskKey(task)]?.name || task.source_id
                    }}</span
                  >
                  <!-- 移除执行任务 -->
                  <el-button text @click.stop="handleRemoveTask(task)">移除</el-button>
                </template>
                <TaskParameters
                  ref="parameterRefs"
                  :disabled="saving || loading || !canSave"
                  v-model="task.parameter"
                  :source="task.source_type"
                  :resource="resources[taskKey(task)]"
                  :trigger-type="form.trigger_type"
                  :body="form.trigger_setting.body ?? []"
                />
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消触发器编辑 -->
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 保存触发器配置 -->
      <el-button v-if="canSave" type="primary" :loading="saving" :disabled="loading || detailFailed" @click="handleSave">{{
        editingId ? '保存' : '创建'
      }}</el-button>
    </template>
  </MkDrawer>
  <SelectApplicationDialog ref="applicationDialogRef" @submit="handleSelectResources(RESOURCE_TYPE.APPLICATION, $event)" />
  <SelectToolDialog
    ref="toolDialogRef"
    :tool-types="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW]"
    @submit="handleSelectResources(RESOURCE_TYPE.TOOL, $event)"
  />
</template>
