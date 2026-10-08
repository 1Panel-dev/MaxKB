<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { KNOWLEDGE_SYNC_TYPE, SCHEDULE_TYPE } from '@/api/enums'
import type { KnowledgeSyncSetting, KnowledgeSyncScheduleType } from '@/api/types'
import { SCHEDULE_OPTION } from '@/constants/schedule'
import { KNOWLEDGE_SYNC_OPTIONS } from '@/constants/knowledge'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { MsgInfo } from '@/utils/message'
import { useKnowledgeDetailContext } from '../../context'
import SyncLogTable from './components/SyncLogTable.vue'

defineOptions({ name: 'KnowledgeScheduledSyncView' })

defineProps<ResourceDetailPageProps>()

// 接口暂未接入，页面只维护本地设置草稿。
const { knowledge } = useKnowledgeDetailContext()
const activeTab = ref('settings')
type SyncSettingDraft = Omit<KnowledgeSyncSetting, 'schedule_type'> & { schedule_type?: KnowledgeSyncScheduleType }
function createDefaultSyncSetting(): SyncSettingDraft {
  return { enabled: false, schedule_type: SCHEDULE_TYPE.DAILY, time: ['00:00'], sync_type: KNOWLEDGE_SYNC_TYPE.INCREMENTAL }
}
const syncSetting = ref<SyncSettingDraft>(createDefaultSyncSetting())
const formRef = useTemplateRef<FormInstance>('formRef')

// 与触发器使用同一套周期级联选项，页面负责配置回写和校验。
const presetScheduleType = ref<KnowledgeSyncScheduleType>()
const scheduleValue = computed<Array<number | string>>({
  get: () => {
    const setting = syncSetting.value
    if (setting.schedule_type === SCHEDULE_TYPE.INTERVAL) {
      return setting.interval_unit && setting.interval_value ? [setting.schedule_type, setting.interval_unit, setting.interval_value] : []
    }
    const time = setting.time?.[0]
    if (!time) return []
    if (setting.schedule_type === SCHEDULE_TYPE.DAILY) return [setting.schedule_type, time]
    const day = setting.days?.[0]
    if (day === undefined) return []
    if (setting.schedule_type === SCHEDULE_TYPE.WEEKLY) return [setting.schedule_type, day, time]
    if (setting.schedule_type === SCHEDULE_TYPE.MONTHLY) return [setting.schedule_type, String(day), time]
    return []
  },
  set: (value) => {
    const setting = syncSetting.value
    if (!value?.length) {
      setting.schedule_type = undefined
      return
    }
    const [scheduleType, dayOrUnit, timeOrInterval] = value
    if (scheduleType === SCHEDULE_TYPE.INTERVAL) {
      setting.schedule_type = scheduleType
      setting.interval_unit = dayOrUnit === 'hours' ? 'hours' : 'minutes'
      setting.interval_value = Number(timeOrInterval)
    } else if (scheduleType === SCHEDULE_TYPE.WEEKLY || scheduleType === SCHEDULE_TYPE.MONTHLY) {
      setting.schedule_type = scheduleType
      setting.days = [Number(dayOrUnit)]
      setting.time = [String(timeOrInterval)]
    } else {
      setting.schedule_type = SCHEDULE_TYPE.DAILY
      setting.time = [String(dayOrUnit)]
    }
  },
})

function handleSwitchScheduleMode() {
  const setting = syncSetting.value
  if (setting.schedule_type === SCHEDULE_TYPE.CRON) setting.schedule_type = presetScheduleType.value
  else {
    presetScheduleType.value = setting.schedule_type
    setting.schedule_type = SCHEDULE_TYPE.CRON
  }
  formRef.value?.clearValidate('schedule_type')
}

const rules: FormRules<SyncSettingDraft> = {
  schedule_type: [
    {
      validator: (_rule, _value, callback) => {
        const setting = syncSetting.value
        let error = ''
        if (!setting.schedule_type) {
          error = '请选择同步周期'
        } else if (setting.schedule_type === SCHEDULE_TYPE.CRON) {
          if (setting.cron_expression?.trim().split(/\s+/).length !== 5) error = '请输入有效的 Cron 表达式（分钟 小时 日期 月份 星期）'
        } else if (setting.schedule_type === SCHEDULE_TYPE.INTERVAL) {
          const minimum = setting.interval_unit === 'hours' ? 1 : 5
          if (!Number.isInteger(setting.interval_value) || (setting.interval_value ?? 0) < minimum)
            error = `同步间隔不能小于 ${minimum} ${setting.interval_unit === 'hours' ? '小时' : '分钟'}`
        } else {
          if (!setting.time?.length || setting.time.some((time) => !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) error = '请选择同步时间'
          if (setting.schedule_type === SCHEDULE_TYPE.WEEKLY || setting.schedule_type === SCHEDULE_TYPE.MONTHLY) {
            const maximum = setting.schedule_type === SCHEDULE_TYPE.WEEKLY ? 7 : 31
            if (!setting.days?.length || setting.days.some((day) => !Number.isInteger(day) || day < 1 || day > maximum)) error = '请选择同步日期'
          }
        }
        callback(error ? new Error(error) : undefined)
      },
      trigger: 'change',
    },
  ],
}

function handleSave() {
  return formRef.value
    ?.validate()
    .then(() => {
      MsgInfo('当前配置仅保留在页面中，暂未接入保存接口')
    })
    .catch(() => {})
}

watch(
  () => knowledge.value?.id,
  () => {
    activeTab.value = 'settings'
    syncSetting.value = createDefaultSyncSetting()
    presetScheduleType.value = undefined
    formRef.value?.clearValidate()
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex-column min-h-0 flex-1">
    <el-tabs v-model="activeTab" class="mb-4 shrink-0">
      <el-tab-pane label="同步设置" name="settings" />
      <el-tab-pane label="同步日志" name="logs" />
    </el-tabs>
    <div v-show="activeTab === 'settings'" class="min-h-40">
      <el-form ref="formRef" :model="syncSetting" :rules="rules" class="max-w-200 pb-6" label-position="top" @submit.prevent>
        <el-form-item>
          <template #label>
            <span>
              启用定时同步
              <span class="ml-2 text-N600">（开启后，系统将按设定周期自动同步知识库中文档）</span>
            </span>
          </template>
          <el-switch v-model="syncSetting.enabled" />
        </el-form-item>
        <div>
          <el-form-item prop="schedule_type">
            <div class="w-full">
              <div class="flex-between mb-2">
                <span class="mk-required">{{ syncSetting.schedule_type === SCHEDULE_TYPE.CRON ? 'Cron 表达式' : '同步周期' }}</span>
                <MkTooltip :content="syncSetting.schedule_type === SCHEDULE_TYPE.CRON ? '切换为周期设置' : '切换为 Cron 表达式'" placement="top">
                  <!-- 切换周期设置与 Cron 表达式 -->
                  <el-button text type="primary" @click="handleSwitchScheduleMode"><MkIcon name="icon_swich" /></el-button>
                </MkTooltip>
              </div>
              <el-cascader
                v-if="syncSetting.schedule_type !== SCHEDULE_TYPE.CRON"
                v-model="scheduleValue"
                :options="SCHEDULE_OPTION"
                :teleported="false"
                class="w-full"
                clearable
                placeholder="请选择同步周期"
              />
              <el-input v-else v-model="syncSetting.cron_expression" placeholder="请输入Cron表达式（如：0 0 1 * *）" />
            </div>
          </el-form-item>
          <el-form-item label="同步方式">
            <el-radio-group v-model="syncSetting.sync_type" class="w-full space-y-2">
              <template v-for="method in KNOWLEDGE_SYNC_OPTIONS" :key="method.value">
                <el-card shadow="hover" class="w-full" :class="{ 'border-primary!': syncSetting.sync_type === method.value }">
                  <el-radio :value="method.value" class="mk-card-radio">
                    <h6>{{ method.label }}</h6>
                    <span class="mt-1 block text-sm text-N600">{{ method.description }}</span>
                  </el-radio>
                </el-card>
              </template>
            </el-radio-group>
          </el-form-item>
        </div>
        <!-- 保存定时同步设置 -->
        <el-button type="primary" class="mt-4" @click="handleSave">保存</el-button>
      </el-form>
    </div>
    <SyncLogTable v-if="activeTab === 'logs'" />
  </div>
</template>
