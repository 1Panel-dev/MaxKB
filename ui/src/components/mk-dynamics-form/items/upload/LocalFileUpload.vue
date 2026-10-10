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
const tipText = computed(
  () => `单次上传最多 ${fileCountLimit.value} 个文件，每个文件最大 ${fileSizeLimit.value} MB${formats.value ? `；支持格式：${formats.value}` : ''}`,
)
</script>

<template>
  <MkDragUpload
    v-model="selectedFiles"
    multiple
    :disabled="inputDisabled"
    :accept="accept"
    :limit="fileCountLimit"
    :size-limit="fileSizeLimit"
    :tip-text="tipText"
  />
</template>
