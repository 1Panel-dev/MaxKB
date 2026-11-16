<script setup lang="ts">
import { computed, inject, provide, useAttrs } from 'vue'
import { useFormDisabled, type UploadRawFile } from 'element-plus'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import type { DragUploadFile, DragUploadHandler } from '@/components/mk-drag-upload/types'
import type { FormField } from '../../type'

defineOptions({ name: 'DynamicFormLocalFileUpload', inheritAttrs: false })

type UploadResponse = string | { data: string }
type UploadResult = (Promise<UploadResponse> & { abort?: () => void }) | { request: Promise<UploadResponse>; abort?: () => void }
type UploadHandler = (file: UploadRawFile, onProgress: (percent: number) => void) => UploadResult

const props = withDefaults(defineProps<{ modelValue?: DragUploadFile[]; formField: FormField }>(), { modelValue: () => [] })
const emit = defineEmits<{ 'update:modelValue': [files: DragUploadFile[]] }>()
const attrs = useAttrs()
const inputDisabled = useFormDisabled()

// 动态表单上传协议适配，进度、重试与取消由多文件组件维护。
const upload = inject<UploadHandler>('upload')
if (upload) {
  provide<DragUploadHandler>('upload', (file, onProgress) => {
    const result = upload(file, onProgress)
    const request = 'request' in result ? result.request : result
    return {
      request: request.then((response) => (typeof response === 'string' ? response : response.data)),
      abort: () => result.abort?.(),
    }
  })
}

// 文件列表与字段配置。
const selectedFiles = computed({
  get: () => props.modelValue ?? [],
  set: (files: DragUploadFile[]) => emit('update:modelValue', files),
})
const fileTypes = computed<string[]>(() => props.formField.attrs?.file_type_list ?? attrs.file_type_list ?? [])
const accept = computed(() => fileTypes.value.map((type) => `.${type.toLowerCase()}`).join(','))
const formats = computed(() => fileTypes.value.map((type) => type.toUpperCase()).join('、'))
const fileSizeLimit = computed(() => Number(props.formField.attrs?.file_size_limit ?? attrs.file_size_limit) || 50)
const fileCountLimit = computed(() => Number(props.formField.attrs?.file_count_limit ?? attrs.file_count_limit) || 100)
</script>

<template>
  <div class="w-full">
    <el-alert type="primary" :closable="false" show-icon class="mb-4!">
      <template #icon><MkIcon name="icon_info_filled" /></template>
      <ol class="list-inside list-decimal space-y-1">
        <li>文件上传前，建议规范文件的分段标识</li>
        <li>每次最多上传 {{ fileCountLimit }} 个文件，每个文件不超过 {{ fileSizeLimit }} MB</li>
      </ol>
    </el-alert>
    <MkDragUpload
      v-model="selectedFiles"
      multiple
      :disabled="inputDisabled"
      :accept="accept"
      :limit="fileCountLimit"
      :size-limit="fileSizeLimit"
      :tip-text="formats ? `支持格式：${formats}` : ''"
    />
  </div>
</template>
