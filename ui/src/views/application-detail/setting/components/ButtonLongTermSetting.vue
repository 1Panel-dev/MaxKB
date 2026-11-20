<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { LongTermSettingData } from '../settings'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { CascaderOption, FormInstance } from 'element-plus'
import { MODEL_STATUS } from '@/api/enums'
import SelectModel from '@/components/business/select-model/index.vue'
import { SCHEDULE_OPTION } from '@/constants/schedule'

defineOptions({ name: 'ButtonLongTermSetting' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ modelOptions: ModelItem[]; providerOptions: ModelProviderItem[] }>()
const setting = defineModel<LongTermSettingData>({ required: true })

// 长期记忆设置：打开时创建草稿，保存后回写配置。
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<LongTermSettingData>({
  long_term_model_id: '',
  long_term_model_params_setting: {},
  long_term_trigger_setting: { rounds: 10 },
  long_term_trigger_type: 'ROUND',
})

// 打开时或模型选项异步返回后，仅为空选择补上首个可用模型。
watch([visible, () => props.modelOptions], ([opened, models]) => {
  if (!opened || formData.value.long_term_model_id) return
  formData.value.long_term_model_id = models.find((model) => model.status === MODEL_STATUS.SUCCESS)?.id ?? ''
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
const triggerOptions = computed(
  () =>
    [
      {
        value: 'ROUND',
        label: t('application.longTermMemory.trigger.rounds'),
        description: t('application.longTermMemory.trigger.roundsDescription'),
      },
      {
        value: 'SCHEDULED',
        label: t('application.longTermMemory.trigger.scheduled'),
        description: t('application.longTermMemory.trigger.scheduledDescription'),
      },
    ] as const,
)
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
  callback(
    typeof value === 'number' && Number.isInteger(value) && value >= 5 && value <= 100
      ? undefined
      : new Error(t('application.longTermMemory.rounds.invalidMessage')),
  )
}

function validateSchedule(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  let options = SCHEDULE_OPTION
  let selectedOption: CascaderOption | undefined
  for (const value of scheduleValue.value) {
    selectedOption = options.find((option) => option.value === value)
    if (!selectedOption) break
    options = selectedOption.children ?? []
  }
  callback(selectedOption && !selectedOption.children?.length ? undefined : new Error(t('application.longTermMemory.period.requiredMessage')))
}

function open() {
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
    callback(new Error(t('common.schedule.cron.invalidMessage')))
    return
  }
  callback()
}

function resetData() {
  formData.value = {
    long_term_model_id: '',
    long_term_model_params_setting: {},
    long_term_trigger_setting: { rounds: 10 },
    long_term_trigger_type: 'ROUND',
  }
  formRef.value?.clearValidate()
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
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" :title="t('application.longTermMemory.title')" @closed="resetData">
    <el-form ref="formRef" :model="formData" :validate-on-rule-change="false" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        :label="t('model.ai.label')"
        prop="long_term_model_id"
        :rules="{ required: true, message: t('application.longTermMemory.model.requiredMessage'), trigger: 'change' }"
      >
        <SelectModel
          v-model="formData.long_term_model_id"
          v-model:model-params="formData.long_term_model_params_setting"
          can-edit-params
          teleported
          :options="modelOptions"
          :provider-options="providerOptions"
          :placeholder="t('application.longTermMemory.model.placeholder')"
        />
      </el-form-item>

      <el-form-item
        :label="t('application.longTermMemory.trigger.label')"
        prop="long_term_trigger_type"
        :rules="{ required: true, message: t('application.longTermMemory.trigger.requiredMessage'), trigger: 'change' }"
      >
        <div class="w-full space-y-2">
          <!-- 选择长期记忆触发方式 -->
          <template v-for="trigger in triggerOptions" :key="trigger.value">
            <MkResourceCard
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
                <div class="mk-gray-card-lg text-N900" @click.stop @keydown.stop>
                  <!-- 定时 -->
                  <template v-if="trigger.value === 'SCHEDULED'">
                    <div class="flex-between mb-2">
                      <span class="mk-required">
                        {{ scheduleMode === 'preset' ? t('application.longTermMemory.period.label') : t('common.schedule.cron.label') }}
                      </span>
                      <!-- 切换周期设置与 Cron 表达式 -->
                      <MkTooltip
                        :content="scheduleMode === 'preset' ? t('common.schedule.switchToCron') : t('common.schedule.switchToPreset')"
                        placement="top"
                      >
                        <el-button text type="primary" @click="scheduleMode = scheduleMode === 'preset' ? 'cron' : 'preset'">
                          <MkIcon name="icon_swich" />
                        </el-button>
                      </MkTooltip>
                    </div>
                    <el-form-item
                      v-if="scheduleMode === 'preset'"
                      prop="long_term_trigger_setting"
                      :rules="{ required: true, validator: validateSchedule, trigger: 'change' }"
                      class="mb-0!"
                    >
                      <el-cascader
                        v-model="scheduleValue"
                        :options="SCHEDULE_OPTION"
                        teleported
                        class="w-full"
                        clearable
                        :placeholder="t('application.longTermMemory.period.placeholder')"
                      />
                    </el-form-item>
                    <el-form-item
                      v-else
                      prop="long_term_trigger_setting.cron_expression"
                      :rules="[
                        { required: true, whitespace: true, message: t('common.schedule.cron.invalidMessage'), trigger: ['blur', 'change'] },
                        { validator: validateCron, trigger: ['blur', 'change'] },
                      ]"
                      class="mb-0!"
                    >
                      <el-input v-model="formData.long_term_trigger_setting.cron_expression" :placeholder="t('common.schedule.cron.placeholder')" />
                    </el-form-item>
                  </template>
                  <!-- 按轮次 -->
                  <el-form-item
                    v-else
                    :label="t('application.longTermMemory.rounds.label')"
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
            </MkResourceCard>
          </template>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消长期记忆设置 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存长期记忆设置 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
