<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, useTemplateRef } from 'vue'
import type { UploadFile, UploadFiles, UploadInstance, UploadRawFile, UploadUserFile } from 'element-plus'
import type { DragUploadFile, DragUploadHandler } from './types'
import FileApi from '@/api/admin/file'
import uploadImage from '@/assets/mk_icon_upload.svg'
import { getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MultipleFileUpload' })

const props = withDefaults(
  defineProps<{
    accept?: string
    disabled?: boolean
    limit?: number
    sizeLimit?: number
    dragText?: string
    selectText?: string
    tipText?: string
  }>(),
  {
    accept: '',
    disabled: false,
    sizeLimit: 100,
    dragText: '将文件拖拽至此区域或',
    selectText: '选择文件',
    tipText: '',
  },
)

const emit = defineEmits<{
  change: [file: UploadFile, fileList: UploadFiles]
  remove: [file: DragUploadFile]
  retry: [file: DragUploadFile]
  exceed: [files: File[], fileList: UploadUserFile[]]
}>()

const upload = inject<DragUploadHandler | undefined>('upload')

const fileList = defineModel<DragUploadFile[]>({ required: true })
const uploadRef = useTemplateRef<UploadInstance>('uploadRef')
const folderInputRef = useTemplateRef<HTMLInputElement>('folderInputRef')

const uploadRequests = new Map<number, () => void>()

async function handleFileChange(file: UploadFile, files: UploadFiles) {
  emit('change', file, files)
  // 等待调用方完成校验与列表回写，仅上传保留的有效文件。
  await nextTick()
  const selectedFile = fileList.value.find((selected) => selected.uid === file.uid)
  if (selectedFile?.status === 'ready' && validateFile(selectedFile)) handleUpload(selectedFile)
}

/* 多文件校验：大小超限保留失败卡片，其他无效文件及重复选择移除。 */
function validateFile(file: DragUploadFile) {
  if (!file.raw || props.disabled) {
    handleRemove(file)
    return false
  }
  if (props.limit !== undefined && fileList.value.length > props.limit) {
    handleExceed([file.raw], fileList.value)
    handleRemove(file)
    return false
  }
  const fileIndex = fileList.value.findIndex((selected) => selected.uid === file.uid)
  if (
    fileList.value
      .slice(0, fileIndex)
      .some((selected) => selected.name === file.name && selected.size === file.size && selected.raw?.lastModified === file.raw?.lastModified)
  ) {
    handleRemove(file)
    return false
  }
  if (file.raw.size > props.sizeLimit * 1024 * 1024) {
    file.status = 'fail'
    file.percentage = 0
    file.errMsg = `大小超限`
    file.canRetry = false
    return false
  }
  const acceptedTypes = props.accept
    .toLowerCase()
    .split(',')
    .map((type) => type.trim())
    .filter(Boolean)
  const filename = file.name.toLowerCase()
  const mimeType = file.raw.type.toLowerCase()
  const accepted = acceptedTypes.some((type) =>
    type.startsWith('.') ? filename.endsWith(type) : type.endsWith('/*') ? mimeType.startsWith(type.slice(0, -1)) : mimeType === type,
  )
  if (acceptedTypes.length && !accepted) {
    if (file.name !== '.DS_Store') MsgWarning('文件格式不支持')
    handleRemove(file)
    return false
  }
  if (file.raw.size === 0) {
    MsgWarning('文件不能为空')
    handleRemove(file)
    return false
  }
  return true
}

/* 注入上传接口，统一维护实际传输进度、失败重试与取消。 */
function handleUpload(file: DragUploadFile) {
  if (props.disabled || !upload || !file.raw || file.uid === undefined || uploadRequests.has(file.uid)) return
  const rawFile = file.raw
  file.status = 'uploading'
  file.percentage = 0
  file.errMsg = ''
  file.canRetry = false
  const uid = file.uid
  // Promise 链同时覆盖上传接口同步抛错和异步请求失败。
  void Promise.resolve()
    .then(() => {
      if (file.status !== 'uploading') return
      const { request, abort } = upload(rawFile, (percent) => {
        file.percentage = Number.isFinite(percent) ? Math.min(100, Math.max(0, percent)) : 0
      })
      uploadRequests.set(uid, abort)
      return request.then((response) => {
        if (file.status !== 'uploading') return
        const split_path = response.split('/')
        file.file_id = split_path[split_path.length - 1]
        file.percentage = 100
        file.status = 'success'
      })
    })
    .catch(() => {
      if (file.status !== 'uploading') return
      file.status = 'fail'
      file.errMsg = '网络失败'
      file.canRetry = true
    })
    .finally(() => uploadRequests.delete(uid))
}

function cancelUpload(file: DragUploadFile) {
  if (file.status === 'uploading') file.status = 'ready'
  if (file.uid === undefined) return
  uploadRequests.get(file.uid)?.()
  uploadRequests.delete(file.uid)
}

onBeforeUnmount(() => {
  for (const file of fileList.value) cancelUpload(file)
})

function handleExceed(files: File[], selectedFiles: UploadUserFile[]) {
  if (props.limit !== undefined) MsgWarning(`每次最多上传 ${props.limit} 个文件`)
  emit('exceed', files, selectedFiles)
}

function clearFiles() {
  for (const file of fileList.value) cancelUpload(file)
  uploadRef.value?.clearFiles()
}

function handleRemove(file: DragUploadFile) {
  cancelUpload(file)
  if (file.status === 'success' && file.file_id) {
    void FileApi.deleteFile(file.file_id).catch(() => {
      // 请求层统一提示删除失败，临时文件仍按有效期清理。
    })
  }
  // 同步清理 ElUpload 的内部列表，避免后续 change 回写已移除的重复文件。
  if (file.uid !== undefined) {
    void Promise.resolve(uploadRef.value?.handleRemove({ ...file, uid: file.uid, status: file.status ?? 'ready' })).catch(() => {
      // 控件已移除该文件时，仍以调用方列表的清理结果为准。
    })
  }
  fileList.value = fileList.value.filter((selected) => selected.uid !== file.uid)
  emit('remove', file)
}

/* 上传汇总与列表排序；尚未上传的文件保留已选择状态。 */
const uploadSummary = computed(() => {
  const summary = { completed: 0, success: 0, error: 0, uploading: 0 }
  for (const file of fileList.value) {
    if (file.status === 'success') summary.success += 1
    if (file.status === 'fail') summary.error += 1
    if (file.status === 'uploading') summary.uploading += 1
  }
  summary.completed = summary.success + summary.error
  return summary
})
const retryFiles = computed(() => fileList.value.filter((file) => file.status === 'fail' && file.canRetry))
const sortedFiles = computed(() => [...fileList.value].sort((first, second) => getFileStatusOrder(first) - getFileStatusOrder(second)))

function getFileStatusOrder(file: DragUploadFile) {
  if (file.status === 'fail') return file.canRetry ? 0 : 1
  if (file.status === 'uploading') return 2
  return 3
}

function handleRetry(file: DragUploadFile) {
  if (props.disabled || file.status !== 'fail' || !file.canRetry) return
  if (upload) handleUpload(file)
  else emit('retry', file)
}

function handleRetryAll() {
  if (props.disabled) return
  // 固定本次失败列表，调用方回写状态不会影响其他文件的重试。
  for (const file of retryFiles.value) handleRetry(file)
}

/* 文件夹选择沿用普通文件的 change 校验和数量限制。 */
function handleOpenFolder() {
  if (!props.disabled) folderInputRef.value?.click()
}

async function handleFolderChange(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  input.value = ''
  if (props.disabled) return

  for (const [index, file] of files.entries()) {
    if (props.disabled) break
    if (props.limit !== undefined && fileList.value.length >= props.limit) {
      handleExceed(files.slice(index), fileList.value)
      break
    }
    uploadRef.value?.handleStart(file as UploadRawFile)
    // 等待 change 与调用方校验回写，按实际保留的文件数量继续添加。
    await nextTick()
  }
}

defineExpose({ clearFiles, handleRemove })
</script>

<template>
  <div class="w-full">
    <el-upload
      ref="uploadRef"
      v-model:file-list="fileList"
      action="#"
      :accept="accept"
      multiple
      :limit="limit"
      :auto-upload="false"
      class="w-full"
      :disabled="disabled"
      drag
      :on-change="handleFileChange"
      :on-exceed="handleExceed"
      :show-file-list="false"
    >
      <div class="mb-2 flex-center">
        <img :src="uploadImage" alt="" />
      </div>
      <div class="el-upload__text">
        <p class="flex-center gap-1">
          {{ dragText }}
          <em>{{ selectText }}</em>
          <!-- 选择文件夹 -->
          <el-button :disabled="disabled" link type="primary" @click.stop="handleOpenFolder">选择文件夹</el-button>
        </p>
        <p v-if="tipText" class="mt-1 text-N500">{{ tipText }}</p>
      </div>
    </el-upload>
    <input ref="folderInputRef" type="file" webkitdirectory multiple hidden @change="handleFolderChange" />

    <template v-if="fileList.length">
      <div class="my-4 flex-between gap-3">
        <p>已完成 {{ uploadSummary.completed }}/{{ fileList.length }}</p>

        <div class="flex-align-center gap-4">
          <MkStatusLabel v-if="uploadSummary.uploading" type="loading" label="上传中" />
          <template v-else-if="uploadSummary.error">
            <MkStatusLabel type="failure" :label="`失败 ${uploadSummary.error} 个`" />
            <!-- 重试所有可重试的失败文件 -->
            <el-button v-if="retryFiles.length" :disabled="disabled" text @click="handleRetryAll">
              <MkIcon name="icon_refresh_outlined" />
              <span>重试</span>
            </el-button>
          </template>
          <MkStatusLabel v-else-if="uploadSummary.success === fileList.length" type="success" label="全部成功" />
        </div>
      </div>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <template v-for="file in sortedFiles" :key="file.uid ?? file.name">
          <el-card class="small relative" shadow="never" :class="{ 'border-danger!': file.status === 'fail' }">
            <div class="flex-align-center gap-3">
              <img :src="getFileIconUrl(file.name)" alt="" class="size-8 shrink-0" />
              <div class="min-w-0 flex-1">
                <p class="truncate" :title="file.name">{{ file.name }}</p>
                <div class="flex-align-center gap-2 text-sm">
                  <span class="shrink-0 text-N500">
                    <template v-if="file.status === 'uploading'">{{ formatFileSize(((file.size ?? 0) * (file.percentage ?? 0)) / 100) }} /</template>
                    {{ formatFileSize(file.size) }}
                  </span>
                  <span v-if="file.status === 'fail'" class="text-danger">
                    {{ file.errMsg }}
                  </span>
                </div>
              </div>
              <div class="flex shrink-0 gap-1">
                <!-- 重试当前失败文件 -->
                <el-button v-if="file.status === 'fail' && file.canRetry" :disabled="disabled" text @click="handleRetry(file)">
                  <MkIcon name="icon_refresh_outlined" />
                </el-button>
                <!-- 删除已选文件 -->
                <el-button :disabled="disabled" text title="删除文件" @click="handleRemove(file)">
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </div>
            </div>
            <el-progress
              v-if="file.status === 'uploading'"
              :percentage="file.percentage ?? 0"
              :stroke-width="4"
              :show-text="false"
              class="absolute inset-x-0 bottom-0"
            />
          </el-card>
        </template>
      </div>
    </template>
  </div>
</template>
