<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { LongTermSetting } from '../types'

defineOptions({ name: 'BaseNodeLongTermSettingDialog' })

defineProps<{ modelOptions: ModelItem[]; providerOptions: ModelProviderItem[] }>()
const emit = defineEmits<{ submit: [setting: LongTermSetting] }>()

const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<LongTermSetting>({
  long_term_model_id: '',
  long_term_model_id_type: 'default',
  long_term_model_params_setting: {},
  long_term_trigger_setting: { rounds: 10 },
  long_term_trigger_type: 'ROUND',
})

const times = Array.from({ length: 24 }, (_, hour) => {
  const value = `${String(hour).padStart(2, '0')}:00`
  return { label: value, value }
})
const scheduleOptions = [
  { label: '每天', value: 'daily', children: times },
  {
    label: '每周',
    value: 'weekly',
    children: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'].map((label, index) => ({ label, value: index + 1, children: times })),
  },
  {
    label: '每月',
    value: 'monthly',
    children: Array.from({ length: 31 }, (_, index) => ({ label: `${index + 1} 日`, value: String(index + 1), children: times })),
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
  },
})

const scheduleValue = computed<Array<number | string>>({
  get: () => {
    const setting = formData.value.long_term_trigger_setting
    if (setting.schedule_type === 'interval') return ['interval', String(setting.interval_unit ?? 'hours'), Number(setting.interval_value ?? 1)]
    if (setting.schedule_type === 'weekly') {
      return ['weekly', Number((setting.days as unknown[] | undefined)?.[0] ?? 1), String((setting.time as unknown[] | undefined)?.[0] ?? '00:00')]
    }
    if (setting.schedule_type === 'monthly') {
      return ['monthly', String((setting.days as unknown[] | undefined)?.[0] ?? '1'), String((setting.time as unknown[] | undefined)?.[0] ?? '00:00')]
    }
    return ['daily', String((setting.time as unknown[] | undefined)?.[0] ?? '00:00')]
  },
  set: (value) => {
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

function open(setting: LongTermSetting) {
  formData.value = cloneDeep(setting)
  if (!formData.value.long_term_trigger_setting || !Object.keys(formData.value.long_term_trigger_setting).length) {
    formData.value.long_term_trigger_setting = { rounds: 10 }
  }
  visible.value = true
}

function changeTriggerType(triggerType: 'ROUND' | 'SCHEDULED') {
  if (triggerType === 'ROUND' && !formData.value.long_term_trigger_setting.rounds) {
    formData.value.long_term_trigger_setting = { rounds: 10 }
  }
  if (triggerType === 'SCHEDULED' && !formData.value.long_term_trigger_setting.schedule_type) {
    formData.value.long_term_trigger_setting = { schedule_type: 'daily', time: ['00:00'] }
  }
}

function validateCron(_rule: unknown, value: unknown, callback: (error?: Error) => void) {
  const fields = String(value ?? '')
    .trim()
    .split(/\s+/)
  if (fields.length !== 5 || fields.some((field) => !field)) {
    callback(new Error('请输入有效的五段 Cron 表达式'))
    return
  }
  callback()
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.long_term_model_id_type === 'custom' && !formData.value.long_term_model_id) {
    callback(new Error('请选择长期记忆模型'))
    return
  }
  callback()
}

function submit() {
  formRef.value?.validate().then(() => {
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="长期记忆设置" width="600">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="长期记忆模型" prop="long_term_model_id" :rules="{ validator: validateModel, trigger: 'change' }">
        <el-radio-group v-model="formData.long_term_model_id_type" class="mb-2">
          <el-radio value="default">默认模型</el-radio>
          <el-radio value="custom">自定义</el-radio>
        </el-radio-group>
        <el-alert v-if="formData.long_term_model_id_type === 'default'" class="w-full" title="使用系统默认 AI 模型" type="info" :closable="false" />
        <ModelSelect
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
        <el-radio-group v-model="formData.long_term_trigger_type" @change="changeTriggerType">
          <el-radio-button value="ROUND">按对话轮次</el-radio-button>
          <el-radio-button value="SCHEDULED">定时执行</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="formData.long_term_trigger_type === 'ROUND'" label="触发间隔（轮）">
        <el-input-number v-model="formData.long_term_trigger_setting.rounds" :max="100" :min="5" />
      </el-form-item>

      <template v-else>
        <el-form-item label="定时方式">
          <el-radio-group v-model="scheduleMode">
            <el-radio value="preset">周期设置</el-radio>
            <el-radio value="cron">Cron 表达式</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="scheduleMode === 'preset'" label="执行周期">
          <el-cascader v-model="scheduleValue" :options="scheduleOptions" :teleported="false" class="w-full" />
        </el-form-item>
        <el-form-item
          v-else
          label="Cron 表达式"
          prop="long_term_trigger_setting.cron_expression"
          :rules="{ validator: validateCron, trigger: 'blur' }"
        >
          <el-input v-model="formData.long_term_trigger_setting.cron_expression" placeholder="例如：0 2 * * *" />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
