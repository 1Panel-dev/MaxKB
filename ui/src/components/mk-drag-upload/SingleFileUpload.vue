<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { UploadFile, UploadFiles, UploadInstance, UploadUserFile } from 'element-plus'
import uploadImage from '@/assets/mk_icon_upload.svg'
import { getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'

defineOptions({ name: 'SingleFileUpload' })

withDefaults(
  defineProps<{
    accept?: string
    disabled?: boolean
    limit?: number
    dragText?: string
    replaceText?: string
    selectText?: string
    tipText?: string
  }>(),
  {
    accept: '',
    disabled: false,
    dragText: '将文件拖至此区域或',
    replaceText: '更换文件',
    selectText: '选择文件上传',
    tipText: '',
  },
)

const emit = defineEmits<{
  change: [file: UploadFile, fileList: UploadFiles]
  remove: [file: UploadUserFile]
  exceed: [files: File[], fileList: UploadUserFile[]]
}>()

defineSlots<{
  download?(props: { file: UploadUserFile }): unknown
}>()

const fileList = defineModel<UploadUserFile[]>({ required: true })
const uploadRef = useTemplateRef<UploadInstance>('uploadRef')
const selectedFile = computed(() => fileList.value[0])

function handleFileChange(file: UploadFile, files: UploadFiles) {
  emit('change', file, files)
}

function handleExceed(files: File[], selectedFiles: UploadUserFile[]) {
  emit('exceed', files, selectedFiles)
}

function clearFiles() {
  uploadRef.value?.clearFiles()
}

function handleRemove(file: UploadUserFile) {
  fileList.value = []
  clearFiles()
  emit('remove', file)
}

defineExpose({ clearFiles, handleRemove })
</script>

<template>
  <div class="w-full">
    <el-upload
      v-if="!selectedFile"
      ref="uploadRef"
      v-model:file-list="fileList"
      action="#"
      :accept="accept"
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
        <p>
          {{ dragText }}
          <em>{{ selectText }}</em>
        </p>
        <p v-if="tipText" class="mt-1 text-N500">{{ tipText }}</p>
      </div>
    </el-upload>

    <div v-if="selectedFile">
      <el-card class="small" shadow="never">
        <div class="flex-align-center gap-2">
          <img :src="getFileIconUrl(selectedFile.name)" alt="" class="w-10 shrink-0" />
          <div class="min-w-0 flex-1">
            <p class="truncate" :title="selectedFile.name">{{ selectedFile.name }}</p>
            <span class="text-sm text-N500">{{ formatFileSize(selectedFile.size) }}</span>
          </div>
          <div class="flex-align-center shrink-0 gap-1">
            <slot name="download" :file="selectedFile" />
            <!-- 删除文件 -->
            <el-button :disabled="disabled" text @click="handleRemove(selectedFile)">
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <div v-if="selectedFile" class="mt-2 flex gap-3">
      <el-upload
        ref="uploadRef"
        v-model:file-list="fileList"
        action="#"
        :accept="accept"
        :limit="limit"
        :auto-upload="false"
        :disabled="disabled"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        :show-file-list="false"
      >
        <!-- 更换文件 -->
        <el-button :disabled="disabled" link type="primary">{{ replaceText }}</el-button>
      </el-upload>
    </div>
  </div>
</template>
