<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { CascaderOption, FormInstance } from 'element-plus'
import SelectModel from '@/components/business/select-model/index.vue'
import type { ModelConfig, ModelItem, ModelProviderItem } from '@/api/types'
import type { LongTermSetting } from '../types'

defineOptions({ name: 'BaseNodeLongTermSetting' })

const props = defineProps<{ modelOptions: ModelItem[]; providerOptions: ModelProviderItem[]; defaultModelSetting?: ModelConfig }>()
const setting = defineModel<LongTermSetting>({ required: true })

// 长期记忆设置：打开时创建草稿，保存后回写配置。
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<LongTermSetting>({
  long_term_model_id: '',
  long_term_model_id_type: 'default',
  long_term_model_params_setting: {},
  long_term_trigger_setting: { rounds: 10 },
  long_term_trigger_type: 'ROUND',
})

// 触发方式卡片与周期选项。
const triggerRounds = computed<number | undefined>({
  get: () => {
    const rounds = formData.value.long_term_trigger_setting.rounds
    return typeof rounds === 'number' ? rounds : undefined
  },
  set: (rounds) => {
    formData.value.long_term_trigger_setting.rounds = rounds
  },
})
const triggerOptions = [
  { value: 'ROUND', label: '按轮次触发', description: '累计到 N 轮后，自动提炼 N 轮对话，生成记忆' },
  { value: 'SCHEDULED', label: '定时触发', description: '到设定时间后，自动提炼周期内所有对话，生成记忆' },
] as const
const scheduleTimes = Array.from({ length: 24 }, (_, hour) => {
  const time = `${String(hour).padStart(2, '0')}:00`
  return { label: time, value: time }
})
const scheduleOptions: CascaderOption[] = [
  { label: '每日', value: 'daily', children: scheduleTimes },
  {
    label: '每周',
    value: 'weekly',
    children: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'].map((label, index) => ({ label, value: index + 1, children: scheduleTimes })),
  },
  {
    label: '每月',
    value: 'monthly',
    children: Array.from({ length: 31 }, (_, index) => ({ label: `${index + 1} 日`, value: String(index + 1), children: scheduleTimes })),
  },
  {
    label: '按间隔',
    value: 'interval',
    children: [
      { label: '小时', value: 'hours', children: Array.from({ length: 24 }, (_, index) => ({ label: `${index + 1} 小时`, value: index + 1 })) },
      { label: '分钟', value: 'minutes', children: Array.from({ length: 60 }, (_, index) => ({ label: `${index + 1} 分钟`, value: index + 1 })) },
    ],
  },
]

const scheduleMode = computed<'cron' | 'preset'>({
  get: () => (formData.value.long_term_trigger_setting.schedule_type === 'cron' ? 'cron' : 'preset'),
  set: (mode) => {
    formData.value.long_term_trigger_setting =
      mode === 'cron' ? { schedule_type: 'cron', cron_expression: '' } : { schedule_type: 'daily', time: ['00:00'] }
    validateTriggerSetting()
  },
})

const scheduleValue = computed<Array<number | string>>({
  get: () => {
    const setting = formData.value.long_term_trigger_setting
    if (setting.schedule_type === 'interval') {
      return typeof setting.interval_unit === 'string' && typeof setting.interval_value === 'number'
        ? ['interval', setting.interval_unit, setting.interval_value]
        : []
    }
    const time = Array.isArray(setting.time) ? setting.time[0] : undefined
    if (typeof time !== 'string') return []
    if (setting.schedule_type === 'daily') return ['daily', time]
    const day = Array.isArray(setting.days) ? setting.days[0] : undefined
    if (day === undefined) return []
    if (setting.schedule_type === 'weekly') return ['weekly', Number(day), time]
    if (setting.schedule_type === 'monthly') return ['monthly', String(day), time]
    return []
  },
  set: (value) => {
    if (!value?.length) {
      formData.value.long_term_trigger_setting = {}
      return
    }
    const scheduleType = value[0]
    if (scheduleType === 'interval') {
      formData.value.long_term_trigger_setting = { schedule_type: 'interval', interval_unit: value[1], interval_value: value[2] }
    } else if (scheduleType === 'weekly' || scheduleType === 'monthly') {
      formData.value.long_term_trigger_setting = { schedule_type: scheduleType, days: [value[1]], time: [value[2]] }
    } else {
      formData.value.long_term_trigger_setting = { schedule_type: 'daily', time: [value[1]] }
    }
  },
})

// 等待当前配置表单挂载后，只校验当前触发方式，清理已隐藏字段的提示。
async function validateTriggerSetting() {
  await nextTick()
  const triggerFields = ['long_term_trigger_setting.rounds', 'long_term_trigger_setting', 'long_term_trigger_setting.cron_expression']
  formRef.value?.clearValidate(triggerFields)
  const activeField =
    formData.value.long_term_trigger_type === 'ROUND' ? triggerFields[0]! : scheduleMode.value === 'cron' ? triggerFields[2]! : triggerFields[1]!
  formRef.value?.validateField(activeField, () => {})
}

function validateRounds(_rule: unknown, value: unknown, callback: (error?: Error) => void) {
  callback(typeof value === 'number' && Number.isInteger(value) && value >= 5 && value <= 100 ? undefined : new Error('请输入 5–100 之间的整数轮次'))
}

function validateSchedule(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  let options = scheduleOptions
  let selectedOption: CascaderOption | undefined
  for (const value of scheduleValue.value) {
    selectedOption = options.find((option) => option.value === value)
    if (!selectedOption) break
    options = selectedOption.children ?? []
  }
  callback(selectedOption && !selectedOption.children?.length ? undefined : new Error('请选择触发周期'))
}

function open() {
  formRef.value?.clearValidate()
  formData.value = cloneDeep(setting.value)
  if (!formData.value.long_term_trigger_setting || !Object.keys(formData.value.long_term_trigger_setting).length) {
    formData.value.long_term_trigger_setting = { rounds: 10 }
  }
  visible.value = true
}

function changeTriggerType(triggerType: 'ROUND' | 'SCHEDULED') {
  if (formData.value.long_term_trigger_type === triggerType) {
    validateTriggerSetting()
    return
  }
  formData.value.long_term_trigger_type = triggerType
  if (triggerType === 'ROUND' && !formData.value.long_term_trigger_setting.rounds) {
    formData.value.long_term_trigger_setting = { rounds: 10 }
  }
  if (triggerType === 'SCHEDULED' && !formData.value.long_term_trigger_setting.schedule_type) {
    formData.value.long_term_trigger_setting = { schedule_type: 'daily', time: ['00:00'] }
  }
  validateTriggerSetting()
}

function validateCron(_rule: unknown, value: unknown, callback: (error?: Error) => void) {
  const fields = String(value ?? '')
    .trim()
    .split(/\s+/)
  if (fields.length !== 5 || fields.some((field) => !field)) {
    callback(new Error('请输入有效的Cron 表达式'))
    return
  }
  callback()
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.long_term_model_id_type === 'custom' && !formData.value.long_term_model_id) {
    callback(new Error('请选择 AI 模型'))
    return
  }
  if (formData.value.long_term_model_id_type === 'default' && !props.defaultModelSetting?.model_id) {
    callback(new Error('请配置默认模型'))
    return
  }
  callback()
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}
</script>

<template>
  <!-- 打开长期记忆设置 -->
  <el-button text type="primary" @click="open">
    <MkIcon name="icon-setting" />
  </el-button>
  <MkDialog v-model="visible" title="长期记忆设置" align-center>
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="AI 模型" prop="long_term_model_id" :rules="{ required: true, validator: validateModel, trigger: 'change' }">
        <el-radio-group v-model="formData.long_term_model_id_type" class="mb-2">
          <el-radio value="default">默认模型</el-radio>
          <el-radio value="custom">自定义</el-radio>
        </el-radio-group>
        <SelectModel
          v-if="formData.long_term_model_id_type === 'default'"
          :model-value="defaultModelSetting?.model_id ?? ''"
          :model-params="defaultModelSetting?.model_params_setting ?? {}"
          disabled
          :options="modelOptions"
          :provider-options="providerOptions"
          placeholder="未配置默认模型"
        />
        <SelectModel
          v-else
          v-model="formData.long_term_model_id"
          v-model:model-params="formData.long_term_model_params_setting"
          can-edit-params
          :options="modelOptions"
          :provider-options="providerOptions"
          placeholder="请选择 AI 模型"
        />
      </el-form-item>

      <el-form-item label="触发方式" prop="long_term_trigger_type" :rules="{ required: true, message: '请选择触发方式', trigger: 'change' }">
        <div class="w-full space-y-2">
          <template v-for="trigger in triggerOptions" :key="trigger.value">
            <MkSourceCard
              :title="trigger.label"
              class="min-h-0!"
              :class="{ 'border-primary!': formData.long_term_trigger_type === trigger.value }"
              :aria-checked="formData.long_term_trigger_type === trigger.value"
              @click="changeTriggerType(trigger.value)"
            >
              <template #icon>
                <TriggerIcon :type="trigger.value" />
              </template>
              <template #subtitle>{{ trigger.description }}</template>
              <template v-if="formData.long_term_trigger_type === trigger.value" #default>
                <div class="mk-gray-card rounded-xl! p-4! text-N900" @click.stop @keydown.stop>
                  <!-- 定时 -->
                  <template v-if="trigger.value === 'SCHEDULED'">
                    <div class="flex-between mb-2">
                      <span class="mk-required">{{ scheduleMode === 'preset' ? '触发周期' : 'Cron 表达式' }}</span>
                      <!-- 切换周期设置与 Cron 表达式 -->
                      <el-tooltip :content="scheduleMode === 'preset' ? '切换为 Cron 表达式' : '切换为周期设置'" placement="top">
                        <el-button text type="primary" @click="scheduleMode = scheduleMode === 'preset' ? 'cron' : 'preset'">
                          <MkIcon name="icon_swich" />
                        </el-button>
                      </el-tooltip>
                    </div>
                    <el-form-item
                      v-if="scheduleMode === 'preset'"
                      prop="long_term_trigger_setting"
                      :rules="{ required: true, validator: validateSchedule, trigger: 'change' }"
                      class="mb-0!"
                    >
                      <el-cascader
                        v-model="scheduleValue"
                        :options="scheduleOptions"
                        :teleported="false"
                        class="w-full"
                        clearable
                        placeholder="请选择触发周期"
                      />
                    </el-form-item>
                    <el-form-item
                      v-else
                      prop="long_term_trigger_setting.cron_expression"
                      :rules="{ required: true, validator: validateCron, trigger: ['blur', 'change'] }"
                      class="mb-0!"
                    >
                      <el-input v-model="formData.long_term_trigger_setting.cron_expression" placeholder="请输入Cron表达式（如：0 0 1 * *）" />
                    </el-form-item>
                  </template>
                  <!-- 按轮次 -->
                  <el-form-item
                    v-else
                    label="触发间隔"
                    prop="long_term_trigger_setting.rounds"
                    :rules="{ required: true, validator: validateRounds, trigger: ['blur', 'change'] }"
                    class="mb-0!"
                  >
                    <el-input-number
                      v-model="triggerRounds"
                      :value-on-clear="5"
                      :max="100"
                      :min="5"
                      :step="1"
                      controls-position="right"
                      align="left"
                    />
                  </el-form-item>
                </div>
              </template>
            </MkSourceCard>
          </template>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消长期记忆设置 -->
      <el-button plain @click="visible = false">取消</el-button>
      <!-- 保存长期记忆设置 -->
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>

<style lang="scss" scoped></style>
