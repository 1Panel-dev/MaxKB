<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type ModelApi from '@/api/admin/workspace/model/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { ModelItem } from '@/api/types'
import { MODEL_STATUS } from '@/api/enums'

defineOptions({ name: 'ModelDownloadStatus' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi; model: ModelItem; refresh: () => Promise<void> }>()

const cancelLoading = ref(false)
let downloadTimer: ReturnType<typeof setInterval> | undefined

function stopDownloadPolling() {
  if (!downloadTimer) return
  clearInterval(downloadTimer)
  downloadTimer = undefined
}

function loadDownloadStatus() {
  return props.api.getModelMeta(props.model.id).then((model) => {
    if (model.status === MODEL_STATUS.DOWNLOAD) return
    stopDownloadPolling()
    return props.refresh()
  })
}

function handleCancelDownload() {
  cancelLoading.value = true
  return props.api
    .putPauseModelDownload(props.model.id)
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
    <LoadingIcon class="h-7 w-7" />
    <span class="mk-dotting my-2 ml-2 text-N600">下载中</span>
    <el-button text type="primary" :loading="cancelLoading" @click.stop="handleCancelDownload"> 取消下载 </el-button>
  </div>
</template>

<style scoped lang="scss">
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
