<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { UploadFile, UploadFiles, UploadUserFile } from 'element-plus'
import SingleFileUpload from './SingleFileUpload.vue'
import MultipleFileUpload from './MultipleFileUpload.vue'
import type { DragUploadFile } from './types'

defineOptions({ name: 'MkDragUpload' })

defineProps<{
  accept?: string
  disabled?: boolean
  multiple?: boolean
  limit?: number
  sizeLimit?: number
  dragText?: string
  replaceText?: string
  selectText?: string
  tipText?: string
}>()

const emit = defineEmits<{
  change: [file: UploadFile, fileList: UploadFiles]
  remove: [file: UploadUserFile]
  retry: [file: DragUploadFile]
  exceed: [files: File[], fileList: UploadUserFile[]]
}>()

defineSlots<{
  download?(props: { file: DragUploadFile }): unknown
}>()

const fileList = defineModel<DragUploadFile[]>({ required: true })
const uploadingCount = computed(() => fileList.value.filter((file) => file.status === 'uploading').length)
const uploadRef = useTemplateRef<InstanceType<typeof SingleFileUpload> | InstanceType<typeof MultipleFileUpload>>('uploadRef')

/* 转发单文件、多文件组件的事件和公开方法。 */
function handleFileChange(file: UploadFile, files: UploadFiles) {
  emit('change', file, files)
}

function handleFileRemove(file: UploadUserFile) {
  emit('remove', file)
}

function handleRetry(file: DragUploadFile) {
  emit('retry', file)
}

function handleExceed(files: File[], filesList: UploadUserFile[]) {
  emit('exceed', files, filesList)
}

function clearFiles() {
  uploadRef.value?.clearFiles()
}

function handleRemove(file: UploadUserFile) {
  uploadRef.value?.handleRemove(file)
}

defineExpose({ clearFiles, handleRemove, uploadingCount })
</script>

<template>
  <component
    :is="multiple ? MultipleFileUpload : SingleFileUpload"
    ref="uploadRef"
    v-model="fileList"
    :accept="accept"
    :disabled="disabled"
    :limit="limit"
    :size-limit="multiple ? sizeLimit : undefined"
    :drag-text="dragText"
    :replace-text="replaceText"
    :select-text="selectText"
    :tip-text="tipText"
    @change="handleFileChange"
    @remove="handleFileRemove"
    @retry="handleRetry"
    @exceed="handleExceed"
  >
    <template v-if="$slots.download" #download="{ file }"><slot name="download" :file="file" /></template>
  </component>
</template>
