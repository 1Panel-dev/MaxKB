<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { UploadFile, UploadFiles, UploadInstance, UploadUserFile } from 'element-plus'
import uploadImage from '@/assets/mk_icon_upload.svg'
import { getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'

defineOptions({ name: 'MkDragUpload' })

withDefaults(
  defineProps<{
    accept?: string
    disabled?: boolean
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

function clearFiles() {
  uploadRef.value?.clearFiles()
}

function handleRemove() {
  if (!selectedFile.value) return

  const file = selectedFile.value
  fileList.value = []
  clearFiles()
  emit('remove', file)
}

defineExpose({ clearFiles })
</script>

<template>
  <div class="w-full">
    <template v-if="selectedFile">
      <div class="flex items-center gap-2 rounded-md border px-3 py-2">
        <img :src="getFileIconUrl(selectedFile.name)" alt="" class="w-10 shrink-0 object-contain" />
        <div class="min-w-0 flex-1">
          <p class="truncate" :title="selectedFile.name">{{ selectedFile.name }}</p>
          <span class="text-sm text-N500">{{ formatFileSize(selectedFile.size) }}</span>
        </div>
        <div class="flex shrink-0 items-center gap-1">
          <slot name="download" :file="selectedFile" />
          <el-button aria-label="删除文件" :disabled="disabled" text @click="handleRemove">
            <MkIcon name="icon_delete-trash_outlined" :size="16" class="text-N600" />
          </el-button>
        </div>
      </div>
      <div class="mt-2 flex gap-3">
        <el-upload
          ref="uploadRef"
          v-model:file-list="fileList"
          action="#"
          :accept="accept"
          :auto-upload="false"
          :disabled="disabled"
          :on-change="handleFileChange"
          :show-file-list="false"
        >
          <el-button :disabled="disabled" link type="primary">更换文件</el-button>
        </el-upload>
      </div>
    </template>

    <el-upload
      v-else
      ref="uploadRef"
      v-model:file-list="fileList"
      action="#"
      :accept="accept"
      :auto-upload="false"
      class="w-full"
      :disabled="disabled"
      drag
      :on-change="handleFileChange"
      :show-file-list="false"
    >
      <div class="mb-2 flex justify-center">
        <img :src="uploadImage" alt="" />
      </div>
      <div class="el-upload__text">
        <p>将文件拖至此区域或 <em>选择文件上传</em></p>
        <p v-if="tipText" class="text-N600">{{ tipText }}</p>
      </div>
    </el-upload>
  </div>
</template>
