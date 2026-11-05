<script setup lang="ts">
import { ref } from 'vue'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{ applicationIds: string[] }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const selectedApplicationIds = ref<string[]>([])
const days = ref(180)
const fileDays = ref(180)

function handleOpenDialog() {
  if (loading.value || !props.applicationIds.length) return
  selectedApplicationIds.value = [...props.applicationIds]
  visible.value = true
}

function handleSubmit() {
  if (loading.value || !selectedApplicationIds.value.length) return
  loading.value = true
  return ApplicationApi.putBatchApplicationCleanTime(selectedApplicationIds.value, days.value, Math.min(fileDays.value, days.value))
    .then(() => {
      MsgSuccess('保存成功')
      visible.value = false
      emit('refresh')
    })
    .finally(() => {
      loading.value = false
    })
}

function resetData() {
  selectedApplicationIds.value = []
  days.value = 180
  fileDays.value = 180
}
</script>

<template>
  <!-- 批量设置对话日志清除策略 -->
  <el-button type="primary" plain :disabled="!applicationIds.length" @click="handleOpenDialog">清除策略</el-button>

  <MkDialog v-model="visible" title="清除策略" @closed="resetData">
    <div class="space-y-4">
      <div class="flex-align-center gap-2">
        <span>删除</span>
        <el-input-number
          v-model="days"
          class="w-40!"
          controls-position="right"
          align="left"
          :min="1"
          :max="100000"
          :value-on-clear="1"
          step-strictly
        />
        <span>天之前的对话记录</span>
      </div>
      <div class="flex-align-center gap-2">
        <span>删除</span>
        <el-input-number
          v-model="fileDays"
          class="w-40!"
          controls-position="right"
          align="left"
          :min="1"
          :max="days"
          :value-on-clear="1"
          step-strictly
        />
        <span>天之前的对话上传的附件</span>
      </div>
    </div>
    <template #footer>
      <!-- 取消清除策略设置 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存批量清除策略 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
