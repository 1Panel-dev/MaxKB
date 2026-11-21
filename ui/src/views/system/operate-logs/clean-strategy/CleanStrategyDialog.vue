<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import OperateLogApi from '@/api/admin/system/operate-log'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CleanStrategyDialog' })
const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const days = ref(180)

function open() {
  visible.value = true
  loading.value = true
  return OperateLogApi.getOperateLogCleanTime()
    .then((cleanTime) => {
      days.value = cleanTime
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSubmit() {
  submitting.value = true
  return OperateLogApi.postOperateLogCleanTime(days.value)
    .then(() => {
      MsgSuccess(t('common.messages.saveSuccess'))
      visible.value = false
    })
    .finally(() => {
      submitting.value = false
    })
}

function resetData() {
  days.value = 180
  loading.value = false
  submitting.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('operateLog.cleanStrategy.title')" @closed="resetData">
    <div v-loading="loading" class="flex-align-center gap-2">
      <span>{{ t('operateLog.cleanStrategy.recordsPrefix') }}</span>
      <el-input-number v-model="days" class="w-40!" controls-position="right" align="left" :min="1" :max="100000" :value-on-clear="1" step-strictly />
      <span>{{ t('operateLog.cleanStrategy.recordsSuffix', days) }}</span>
    </div>

    <template #footer>
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :loading="submitting" :disabled="loading" @click="handleSubmit">{{ t('common.actions.comfirm') }}</el-button>
    </template>
  </MkDialog>
</template>
