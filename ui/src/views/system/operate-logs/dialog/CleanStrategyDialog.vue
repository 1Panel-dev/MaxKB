<script setup lang="ts">
import { ref } from 'vue'
import OperateLogApi from '@/api/admin/system/operate-log'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CleanStrategyDialog' })

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
      MsgSuccess('保存成功')
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
  <MkDialog v-model="visible" title="清除策略" @closed="resetData">
    <div v-loading="loading" class="flex items-center gap-2">
      <span>删除</span>
      <el-input-number
        v-model="days"
        class="w-40!"
        controls-position="right"
        :min="1"
        :max="100000"
        :value-on-clear="1"
        step-strictly
      />
      <span>天之前的对话记录</span>
    </div>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" :disabled="loading" @click="handleSubmit">
        确认
      </el-button>
    </template>
  </MkDialog>
</template>
