<script setup lang="ts">
import { ref } from 'vue'
import ChatLogApi from '@/api/admin/workspace/application/chat-log'
import { MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'ChatLogCleanStrategyDialog' })
const props = defineProps<{ applicationId: string }>()
const { application, refreshApplicationDetail } = useApplicationDetailContext()

// 读取成功后打开弹窗，查询与保存共用 loading
const visible = ref(false)
const loading = ref(false)
const days = ref(180)
const fileDays = ref(180)

function open() {
  if (loading.value) return
  loading.value = true
  return refreshApplicationDetail(false)
    .then(() => {
      const detail = application.value
      if (!detail) return
      days.value = detail.clean_time ?? 180
      fileDays.value = detail.file_clean_time ?? days.value
      visible.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSubmit() {
  if (loading.value) return
  loading.value = true
  return ChatLogApi.putChatLogCleanTime(props.applicationId, days.value, Math.min(fileDays.value, days.value))
    .then(() => {
      return refreshApplicationDetail(false).then(() => {
        MsgSuccess('保存成功')
        visible.value = false
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function resetData() {
  days.value = 180
  fileDays.value = 180
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="清除策略" @closed="resetData">
    <div v-loading="loading" class="space-y-4">
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
      <!-- 保存清除策略 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
