<template>
  <el-dialog
    :title="$t('views.chatLog.buttons.clearStrategy')"
    v-model="dialogVisible"
    width="520px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-alert
      :title="$t('views.application.batchClearStrategyTip')"
      type="info"
      :closable="false"
      class="mb-16"
    />
    <div class="clean-strategy-row mb-16">
      <span>{{ $t('common.delete') }}</span>
      <el-input-number
        v-model="days"
        controls-position="right"
        :min="1"
        :max="100000"
        :value-on-clear="0"
        step-strictly
        class="clean-strategy-number"
      />
      <span>{{ $t('views.chatLog.daysText') }}</span>
    </div>
    <div class="clean-strategy-row">
      <span>{{ $t('common.delete') }}</span>
      <el-input-number
        v-model="fileDays"
        controls-position="right"
        :min="1"
        :max="days"
        :value-on-clear="0"
        step-strictly
        class="clean-strategy-number"
      />
      <span>{{ $t('views.chatLog.fileDaysText') }}</span>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ApplicationApi from '@/api/application/application'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'

const emit = defineEmits(['refresh'])

const loading = ref(false)
const dialogVisible = ref(false)
const days = ref(180)
const fileDays = ref(180)
const selectedIds = ref<string[]>([])

function open(idList: string[]) {
  selectedIds.value = [...idList]
  days.value = 180
  fileDays.value = 180
  dialogVisible.value = true
}

function submitHandle() {
  if (fileDays.value > days.value) {
    fileDays.value = days.value
  }
  ApplicationApi.putMulCleanTime(
    {
      id_list: selectedIds.value,
      clean_time: days.value,
      file_clean_time: fileDays.value,
    },
    loading,
  ).then(() => {
    MsgSuccess(t('common.saveSuccess'))
    dialogVisible.value = false
    emit('refresh')
  })
}

defineExpose({ open })
</script>

<style scoped lang="scss">
.clean-strategy-row {
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 32px;
}

.clean-strategy-number {
  width: 110px;
}
</style>
