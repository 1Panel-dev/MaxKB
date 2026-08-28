<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { ModelItem } from '@/api/types'
import { MODEL_STATUS } from '@/api/enums'
import ModelApi from '@/api/admin/workspace/model/model'

defineOptions({ name: 'ModelDownloadStatus' })

const props = defineProps<{
  model: ModelItem
  refresh: () => Promise<void>
}>()

const cancelLoading = ref(false)
let downloadTimer: ReturnType<typeof setInterval> | undefined

function stopDownloadPolling() {
  if (!downloadTimer) return
  clearInterval(downloadTimer)
  downloadTimer = undefined
}

function loadDownloadStatus() {
  return ModelApi.getModelMeta(props.model.id).then((model) => {
    if (model.status === MODEL_STATUS.DOWNLOAD) return
    stopDownloadPolling()
    return props.refresh()
  })
}

function handleCancelDownload() {
  cancelLoading.value = true
  return ModelApi.putPauseModelDownload(props.model.id)
    .then(() => {
      stopDownloadPolling()
      return props.refresh()
    })
    .finally(() => {
      cancelLoading.value = false
    })
}

onMounted(() => {
  downloadTimer = setInterval(loadDownloadStatus, 6000)
})

onBeforeUnmount(() => stopDownloadPolling())
</script>

<template>
  <div class="model-download-status bg-white/94">
    <div
      v-loading="true"
      aria-label="下载中"
      class="download-spinner h-7 w-7"
      element-loading-background="transparent"
      role="status"
    ></div>
    <span class="mk-dotting my-2 ml-2 text-N600">下载中</span>
    <el-button text type="primary" :loading="cancelLoading" @click.stop="handleCancelDownload">
      取消下载
    </el-button>
  </div>
</template>

<style scoped lang="scss">
.download-spinner {
  --el-loading-spinner-size: 24px;

  :deep(.el-loading-spinner .path) {
    stroke-width: 4px;
  }
}

.model-download-status {
  align-items: center;
  border-radius: var(--el-card-border-radius);
  display: flex;
  flex-direction: column;
  inset: 0;
  justify-content: center;
  position: absolute;
  z-index: 20;
}
</style>
