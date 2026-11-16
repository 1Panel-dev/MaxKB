<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, inject, ref, useAttrs } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { MsgWarning } from '@/utils/message'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl, isImage, isAudio, isVideo } from '@/utils/icon'
import { useFormDisabled } from 'element-plus'

import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import MkAudio from '@/components/global/mk-media-preview/MkAudio.vue'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
const inputDisabled = useFormDisabled()
const attrs = useAttrs() as DynamicFormValue
const upload = inject('upload') as DynamicFormValue
const props = withDefaults(defineProps<{ modelValue?: DynamicFormValue; formField: FormField }>(), { modelValue: () => [] })
const emit = defineEmits(['update:modelValue'])

const deleteFile = (file: DynamicFormValue) => {
  if (inputDisabled.value) return
  fileArray.value = modelValueProxy.value.filter((attachment: DynamicFormValue) => attachment.file_id !== file.file_id)
  emit('update:modelValue', fileArray.value)
}

const modelValueProxy = computed({
  get: () => {
    if (!props.modelValue) {
      emit('update:modelValue', [])
    }
    return props.modelValue
  },
  set: (v: DynamicFormValue[]) => {
    emit('update:modelValue', v)
  },
})
const fileArray = ref<DynamicFormValue>([])

// 按原顺序展示附件，类型仅决定预览方式。
const attachments = computed(() =>
  (modelValueProxy.value || []).map((file: DynamicFormValue) => ({
    ...file,
    status: 'success' as const,
    url: file.url || getFileUrl(file.file_id),
    kind: isImage(file.name) ? 'image' : isAudio(file.name) ? 'audio' : isVideo(file.name) ? 'video' : 'file',
  })),
)
const imageSources = computed(() =>
  attachments.value.filter((file: DynamicFormValue) => file.kind === 'image').map((file: DynamicFormValue) => file.url),
)

const loading = ref<boolean>(false)

const uploadFile = async (file: DynamicFormValue, fileList: DynamicFormValue[]) => {
  fileList.splice(fileList.indexOf(file), 1)
  if (fileArray.value.find((f: DynamicFormValue) => f.name === file.name)) {
    MsgWarning('文件名重复')

    return
  }
  const maxFileSize = (props.formField as DynamicFormValue).max_file_size
  if (file.size / 1024 / 1024 > maxFileSize) {
    MsgWarning('文件大小不能超过 ' + maxFileSize + 'MB')
    return
  }

  if (fileList.length > attrs.limit) {
    MsgWarning('最多只能上传 ' + attrs.limit + ' 个文件')
    return
  }
  upload(file.raw, loading).then((ok: DynamicFormValue) => {
    const pathSegments = ok.data.split('/')
    const fileId = pathSegments[pathSegments.length - 1]
    fileArray.value?.push({ name: file.name, file_id: fileId, size: file.size })
    emit('update:modelValue', fileArray.value)
  })
}
</script>

<template>
  <!-- 上传表单附件 -->
  <el-upload
    v-if="!inputDisabled"
    v-loading="loading"
    action="#"
    v-bind="$attrs"
    :auto-upload="false"
    :on-change="(file: DynamicFormValue, fileList: DynamicFormValue) => uploadFile(file, fileList)"
    v-model:file-list="modelValueProxy"
    multiple
    :show-file-list="false"
  >
    <el-button plain>
      <MkIcon name="icon_upload_outlined" />
      <span>上传文件</span>
    </el-button>
  </el-upload>
  <div v-if="attachments.length" class="mt-2 flex flex-wrap w-full gap-2">
    <div v-for="file in attachments" :key="file.file_id" class="min-w-0" :class="file.kind === 'image' ? 'shrink-0' : 'w-full'">
      <!-- 查看图片，可编辑时允许删除 -->
      <ImageUploadCard
        v-if="file.kind === 'image'"
        :file="file"
        :src="file.url"
        :size="104"
        :show-remove="!inputDisabled"
        :preview-src-list="imageSources"
        :initial-index="imageSources.indexOf(file.url)"
        @remove="deleteFile(file)"
      />
      <!-- 播放音视频，或在新标签页打开及下载文件 -->
      <component
        :is="file.kind === 'audio' ? MkAudio : file.kind === 'video' ? MkVideo : 'a'"
        v-else
        v-bind="
          file.kind === 'audio' || file.kind === 'video'
            ? { src: file.url, name: file.name }
            : { href: file.url || undefined, target: '_blank', rel: 'noopener noreferrer', download: file.name }
        "
        class="block min-w-0"
      >
        <el-card shadow="never" class="small cursor-pointer">
          <div class="flex-align-center gap-2">
            <img :src="getFileIconUrl(file.name)" alt="" width="24" class="shrink-0" />
            <span class="min-w-0 flex-1 truncate" :title="file.name">{{ file.name }}</span>
            <!-- 删除附件，不触发文件打开或媒体播放 -->
            <el-button v-if="!inputDisabled" text class="shrink-0" @click.stop.prevent="deleteFile(file)">
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </div>
        </el-card>
      </component>
    </div>
  </div>
</template>
