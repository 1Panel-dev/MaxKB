<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import type { ResourceTrigger, ResourceTriggerResource, TriggerSetting } from '@/api/types'
import { TRIGGER_TYPE, TRIGGER_SCHEDULE_TYPE } from '@/api/enums'
import { MsgSuccess } from '@/utils/message'
import TriggerFormDrawer from '../trigger-form/TriggerFormDrawer.vue'

const props = defineProps<{ api: typeof ResourceTriggerApi; resource: ResourceTriggerResource }>()
const emit = defineEmits<{ closed: [] }>()

/* 当前资源的触发器列表 */
const visible = ref(false)
const loading = ref(false)
const triggersData = ref<ResourceTrigger[]>([])
function loadTriggers() {
  loading.value = true
  return props.api
    .getResourceTriggerList(props.resource)
    .then((result) => {
      triggersData.value = result
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
function open() {
  triggersData.value = []
  visible.value = true
  return loadTriggers()
}

function getScheduleLabel(setting: TriggerSetting) {
  const times = setting.time?.join('、') || '-'
  switch (setting.schedule_type) {
    case TRIGGER_SCHEDULE_TYPE.DAILY:
      return `每日/${times}`
    case TRIGGER_SCHEDULE_TYPE.WEEKLY: {
      const weekdays = ['日', '一', '二', '三', '四', '五', '六']
      return `每周${setting.days?.map((day) => weekdays[Number(day) % 7]).join('、') || '-'}/${times}`
    }
    case TRIGGER_SCHEDULE_TYPE.MONTHLY:
      return `每月${setting.days?.join('、') || '-'}日/${times}`
    case TRIGGER_SCHEDULE_TYPE.INTERVAL:
      return `每隔${setting.interval_value ?? '-'}${setting.interval_unit === 'hours' ? '小时' : '分钟'}`
    case TRIGGER_SCHEDULE_TYPE.CRON:
      return setting.cron_expression || '-'
    default:
      return '-'
  }
}

/* 创建、编辑复用同一表单抽屉，关闭后释放 */
const formMounted = ref(false)
const triggerFormRef = useTemplateRef<InstanceType<typeof TriggerFormDrawer>>('triggerFormRef')
function handleOpenForm(triggerId?: string) {
  if (loading.value) return
  formMounted.value = true
  return nextTick(() => triggerFormRef.value?.open(triggerId))
}
function handleFormClosed() {
  formMounted.value = false
}
function handleRemoveTrigger(trigger: ResourceTrigger) {
  if (loading.value) return
  loading.value = true
  return props.api
    .deleteResourceTrigger(props.resource, trigger.id)
    .then(() => {
      MsgSuccess('移除成功')
      return loadTriggers()
    })
    .finally(() => {
      loading.value = false
    })
}
defineExpose({ open })
</script>

<template>
  <MkDialog class="resource-trigger-dialog" v-model="visible" @closed="emit('closed')">
    <template #header>
      <div class="flex-between">
        <h4>触发器</h4>
        <div class="flex-align-center">
          <!-- 添加触发器 -->
          <el-button text :disabled="loading" @click="handleOpenForm()" class="text-N900!"
            ><MkIcon name="icon_add_outlined" />
            <span>添加</span>
          </el-button>
          <el-divider direction="vertical" class="ml-3! mr-4!" />
        </div>
      </div>
    </template>
    <div v-loading="loading" class="min-h-30">
      <div class="space-y-2">
        <template v-for="trigger in triggersData" :key="trigger.id">
          <el-card shadow="never" class="small">
            <div class="flex-between gap-3">
              <div class="flex-align-center min-w-0 flex-1 gap-2">
                <TriggerIcon :type="trigger.trigger_type" :size="20" class="shrink-0" />
                <span class="truncate" :title="trigger.name">{{ trigger.name }}</span>
              </div>
              <span v-if="trigger.trigger_type === TRIGGER_TYPE.SCHEDULED" class="text-N600" :title="getScheduleLabel(trigger.trigger_setting)">{{
                getScheduleLabel(trigger.trigger_setting)
              }}</span>
              <div class="flex-align-center shrink-0">
                <!-- 编辑触发器 -->

                <el-button text :disabled="loading" @click="handleOpenForm(trigger.id)"><MkIcon name="icon_edit_outlined" /></el-button>

                <!-- 移除当前资源的触发器 -->

                <el-button text :disabled="loading" @click="handleRemoveTrigger(trigger)"><MkIcon name="icon_close_outlined" /></el-button>
              </div>
            </div>
          </el-card>
        </template>
      </div>
      <MkEmpty v-if="!triggersData.length" />
    </div>
  </MkDialog>
  <TriggerFormDrawer
    v-if="formMounted"
    ref="triggerFormRef"
    :resource="resource"
    :resource-api="api"
    @refresh="loadTriggers"
    @closed="handleFormClosed"
  />
</template>

<style scoped lang="scss"></style>
