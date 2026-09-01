<template>
  <el-dialog
    align-center
    :title="$t('views.application.longTermMemory.setting')"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      label-position="top"
      ref="paramFormRef"
      :model="form"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        v-if="modelSettingEnable"
        :label="$t('views.application.longTermMemory.title')"
        prop="long_term_model_id"
        :rules="modelIdRules"
      >
        <div class="w-full">
          <el-radio-group v-model="form.long_term_model_id_type" class="mb-8">
            <el-radio
              :label="$t('views.application.longTermMemory.defaultModel')"
              value="default"
            />
            <el-radio :label="$t('views.application.longTermMemory.custom')" value="custom" />
          </el-radio-group>
        </div>
        <DefaultModelDisplay
          v-if="form.long_term_model_id_type === 'default'"
          type="LLM"
          :options="modelOptions"
        />
        <div v-else class="flex-between w-full">
          <ModelSelect
            v-model="form.long_term_model_id"
            :placeholder="$t('views.application.form.aiModel.placeholder')"
            :options="modelOptions"
            @change="long_term_model_change"
            @submitModel="getSelectModel"
            showFooter
            :model-type="'LLM'"
          >
          </ModelSelect>
          <el-button
            class="ml-8"
            :disabled="!form.long_term_model_id"
            @click="openLongTermParamSettingDialog"
          >
            <el-icon>
              <Operation />
            </el-icon>
          </el-button>
        </div>
      </el-form-item>
      <el-form-item
        :label="$t('views.application.longTermMemory.triggerType')"
        prop="trigger_type"
        :rules="{
          message: $t('common.selectPlaceholder'),
          trigger: 'blur',
          required: true,
        }"
      >
        <el-card
          shadow="never"
          class="mb-16 w-full cursor"
          :class="form.trigger_type === 'ROUND' ? 'border-active' : ''"
          @click="changeTriggerType('ROUND')"
        >
          <div class="flex align-center line-height-22">
            <el-avatar shape="square" class="avatar-orange" :size="32">
              <img src="@/assets/trigger/icon_event.svg" style="width: 58%" alt="" />
            </el-avatar>
            <div class="ml-12">
              <h5>{{ $t('views.application.longTermMemory.roundTrigger') }}</h5>
              <el-text type="info" class="color-secondary font-small"
                >{{ $t('views.application.longTermMemory.roundTriggerTip') }}
              </el-text>
            </div>
          </div>
          <el-card v-if="form.trigger_type === 'ROUND'" shadow="never" class="card-never mt-16">
            <el-form-item :label="$t('views.application.longTermMemory.triggerInterval')" required>
              <el-input-number
                v-model="form.trigger_setting.rounds"
                :value-on-clear="0"
                :min="5"
                :max="100"
              />
            </el-form-item>
          </el-card>
        </el-card>
        <el-card
          shadow="never"
          class="w-full cursor"
          :class="form.trigger_type === 'SCHEDULED' ? 'border-active' : ''"
          @click="changeTriggerType('SCHEDULED')"
        >
          <div class="flex align-center line-height-22">
            <el-avatar shape="square" :size="32">
              <img src="@/assets/trigger/icon_scheduled.svg" style="width: 58%" alt="" />
            </el-avatar>
            <div class="ml-12">
              <h5>{{ $t('views.application.longTermMemory.scheduledTrigger') }}</h5>
              <el-text type="info" class="color-secondary font-small"
                >{{ $t('views.application.longTermMemory.scheduledTriggerTip') }}
              </el-text>
            </div>
          </div>

          <el-card
            v-if="form.trigger_type === 'SCHEDULED'"
            shadow="never"
            class="card-never mt-16 w-full"
          >
            <div class="flex-between">
              <p style="margin-top: -8px">
                {{
                  form.trigger_setting.schedule_type === 'cron'
                    ? $t('views.trigger.triggerCycle.cronExpression')
                    : $t('views.trigger.triggerCycle.title')
                }}
              </p>
              <el-tooltip
                :content="
                  form.trigger_setting.schedule_type === 'cron'
                    ? $t('views.trigger.triggerCycle.switchCycle')
                    : $t('views.trigger.triggerCycle.switchCron')
                "
                placement="top"
                effect="light"
              >
                <el-button text @click.stop="switchScheduleType">
                  <el-icon>
                    <Switch />
                  </el-icon>
                </el-button>
              </el-tooltip>
            </div>

            <el-cascader
              v-if="form.trigger_setting.schedule_type !== 'cron'"
              v-model="scheduled"
              :options="triggerCycleOptions"
              @change="handleChangeScheduled"
              style="width: 100%"
            />
            <el-input
              v-else
              v-model="form.trigger_setting.cron_expression"
              :placeholder="t('views.trigger.triggerCycle.placeholder')"
              clearable
              @blur="validateCron"
              @input="validateCron"
            />
            <div v-if="cronError" class="el-form-item__error">{{ cronError }}</div>
          </el-card>
        </el-card>
      </el-form-item>
    </el-form>

    <AIModeParamSettingDialog
      ref="longTermModeParamSettingDialogRef"
      @refresh="refreshModelParams"
    />

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { triggerCycleOptions } from '@/utils/trigger.ts'
import { t } from '@/locales'
import { cloneDeep, groupBy } from 'lodash'
import { isValidCron } from 'cron-validator'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import DefaultModelDisplay from '@/workflow/common/DefaultModelDisplay.vue'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'

const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const emit = defineEmits(['refresh'])
const dialogVisible = ref(false)
const paramFormRef = ref()
const loading = ref(false)
const modelOptions = ref<any>(null)
const longTermModeParamSettingDialogRef = ref()
const modelSettingEnable = ref(false)
const form = ref<any>({
  trigger_type: 'ROUND',
  trigger_setting: {
    rounds: 10,
  },
  long_term_model_id_type: 'default',
  long_term_model_id: '',
})

const lastPresetSetting = ref<any>(null)
const cronError = ref('')

const changeTriggerType = (type: string) => {
  form.value.trigger_type = type
}

const modelIdRules = computed(() => ({
  validator: (rule: any, value: any, callback: any) => {
    if (form.value.long_term_model_id_type === 'custom' && !form.value.long_term_model_id) {
      callback(new Error(t('views.application.longTermMemory.modelRequiredMessage')))
    } else {
      callback()
    }
  },
  trigger: 'change',
}))

function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'LLM',
          workspace_id: form.value?.workspace_id,
        }
      : {
          model_type: 'LLM',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
    .catch(() => {})
}

const long_term_model_change = (model_id?: string) => {
  form.value.long_term_model_id = model_id
  if (model_id) {
    longTermModeParamSettingDialogRef.value?.reset_default(model_id, form.value.application_id)
  } else {
    form.value.long_term_model_params_setting = {}
  }
}

function refreshModelParams(data: any) {
  form.value.long_term_model_params_setting = data
}

function openLongTermParamSettingDialog() {
  if (form.value.long_term_model_id) {
    longTermModeParamSettingDialogRef.value?.open(
      form.value.long_term_model_id,
      form.value.application_id,
      form.value.long_term_model_params_setting,
    )
  }
}

const validateCron = () => {
  const cron = form.value.trigger_setting.cron_expression?.trim()
  if (!cron) {
    cronError.value = ''
    return
  }
  const fields = cron.split(/\s+/)
  if (fields.length !== 5 || !isValidCron(cron)) {
    cronError.value = t('views.application.longTermMemory.cronExpressionInvalid')
  } else {
    cronError.value = ''
  }
}

function switchScheduleType() {
  const currentType = form.value.trigger_setting.schedule_type || 'daily'
  const isCron = currentType === 'cron'

  if (!isCron) {
    lastPresetSetting.value = cloneDeep({
      schedule_type: form.value.trigger_setting.schedule_type,
      interval_unit: form.value.trigger_setting.interval_unit,
      interval_value: form.value.trigger_setting.interval_value,
      days: form.value.trigger_setting.days,
      time: form.value.trigger_setting.time,
    })

    form.value.trigger_setting.schedule_type = 'cron'
    form.value.trigger_setting.interval_unit = undefined
    form.value.trigger_setting.interval_value = undefined
    form.value.trigger_setting.days = undefined
    form.value.trigger_setting.time = undefined
    return
  }
  cronError.value = ''
  const backup = lastPresetSetting.value
  form.value.trigger_setting.schedule_type = backup?.schedule_type || 'daily'
  form.value.trigger_setting.interval_unit = backup?.interval_unit
  form.value.trigger_setting.interval_value = backup?.interval_value
  form.value.trigger_setting.days = backup?.days
  form.value.trigger_setting.time = backup?.time
}

const handleChangeScheduled = (v: Array<any>) => {
  scheduled.value = v
}

const scheduled = computed({
  get: () => {
    const schedule_type = form.value.trigger_setting.schedule_type
    if (schedule_type) {
      if (schedule_type === 'interval') {
        const interval_value = form.value.trigger_setting.interval_value
        const interval_unit = form.value.trigger_setting.interval_unit
        return [schedule_type, interval_unit, interval_value].filter((item) => item !== undefined)
      } else {
        const days = form.value.trigger_setting.days
          ? form.value.trigger_setting.days[0]
          : undefined
        const time = form.value.trigger_setting.time
          ? form.value.trigger_setting.time[0]
          : undefined
        if (schedule_type == 'daily') {
          return [schedule_type, time].filter((item) => item !== undefined)
        }
        return [schedule_type, days, time].filter((item) => item !== undefined)
      }
    }
    return []
  },
  set: (value) => {
    const schedule_type = value[0]
    form.value.trigger_setting.schedule_type = schedule_type
    if (schedule_type == 'interval') {
      form.value.trigger_setting.interval_unit = value[1]
      form.value.trigger_setting.interval_value = value[2]
    } else {
      if (schedule_type == 'daily') {
        form.value.trigger_setting.time = [value[1]]
      } else {
        form.value.trigger_setting.days = [value[1]]
        form.value.trigger_setting.time = [value[2]]
      }
    }
  },
})

const open = (data: any) => {
  dialogVisible.value = true
  const { trigger_type, trigger_setting, long_term_model_id_type, long_term_model_id, model_params_setting, application_id, workspace_id, model_setting_enable } = data || {}
  modelSettingEnable.value = model_setting_enable ?? false
  form.value.application_id = application_id
  form.value.workspace_id = workspace_id
  form.value.long_term_model_id_type = long_term_model_id_type ?? 'default'
  form.value.long_term_model_id = long_term_model_id
  form.value.long_term_model_params_setting = model_params_setting
  if (trigger_setting && trigger_setting.rounds) {
    form.value.trigger_setting = trigger_setting
  } else {
    form.value.trigger_setting = { rounds: 10 }
  }
  form.value.trigger_type = trigger_type ?? 'ROUND'
  if (modelSettingEnable.value) {
    getSelectModel()
  }
}

const submit = () => {
  paramFormRef.value.validate((valid: any) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>

<style lang="scss" scoped></style>
