<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, inject, ref, useAttrs } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { downloadByURL, getAttrsArray, getFileUrl } from '@/utils/common'
import { getFileExtension, getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'

import { useFormDisabled } from 'element-plus'
const inputDisabled = useFormDisabled()
const attrs = useAttrs() as DynamicFormValue
const upload = inject('upload') as DynamicFormValue
const props = withDefaults(defineProps<{ modelValue?: DynamicFormValue; formField: FormField }>(), { modelValue: () => [] })
const emit = defineEmits(['update:modelValue'])

const deleteFile = (file: DynamicFormValue) => {
  if (inputDisabled.value) {
    return
  }
  fileArray.value = fileArray.value.filter((f: DynamicFormValue) => f.uid !== file.uid)
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

const imageExtensions = ['JPG', 'JPEG', 'PNG', 'GIF', 'BMP']
const videoExtensions = ['MP4', 'AVI', 'MKV', 'MOV', 'FLV', 'WMV']
const audioExtensions = ['MP3', 'WAV', 'OGG', 'AAC', 'M4A']
const ofType = (exts: string[]) => (f: DynamicFormValue) => exts.includes(getFileExtension(f?.name || '').toUpperCase())

const filesWithUrl = computed(() => (modelValueProxy.value || []).map((f: DynamicFormValue) => ({ ...f, url: f.url || getFileUrl(f.file_id) })))
const images = computed(() => filesWithUrl.value.filter(ofType(imageExtensions)))
const audioFiles = computed(() => filesWithUrl.value.filter(ofType(audioExtensions)))
const videoFiles = computed(() => filesWithUrl.value.filter(ofType(videoExtensions)))
// 非图片/音频/视频的（文档、压缩包等）统一走下载卡片
const downloadFiles = computed(() => filesWithUrl.value.filter((f: DynamicFormValue) => !ofType([...imageExtensions, ...audioExtensions, ...videoExtensions])(f)))

function downloadFile(item: DynamicFormValue) {
  downloadByURL(item.url, item.name)
}

const loading = ref<boolean>(false)

const uploadFile = async (file: DynamicFormValue, fileList: DynamicFormValue[]) => {
  fileList.splice(fileList.indexOf(file), 1)
  if (fileArray.value.find((f: DynamicFormValue) => f.name === file.name)) {
    ElMessage.warning('文件名重复')

    return
  }
  const maxFileSize = (props.formField as DynamicFormValue).max_file_size
  if (file.size / 1024 / 1024 > maxFileSize) {
    ElMessage.warning('文件大小不能超过 ' + maxFileSize + 'MB')
    return
  }

  if (fileList.length > attrs.limit) {
    ElMessage.warning('最多只能上传 ' + attrs.limit + ' 个文件')
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
  <el-upload
    style="width: 100%"
    v-loading="loading"
    action="#"
    v-bind="$attrs"
    :auto-upload="false"
    :on-change="(file: DynamicFormValue, fileList: DynamicFormValue) => uploadFile(file, fileList)"
    v-model:file-list="modelValueProxy"
    multiple
    :show-file-list="false"
  >
    <el-button type="primary">上传文件</el-button>
  </el-upload>
  <el-space wrap class="w-full media-file-width upload_content mt-16" v-if="!inputDisabled">
    <template v-for="(file, index) in modelValueProxy" :key="index">
      <el-card style="--el-card-padding: 0" shadow="never">
        <div class="flex-between" :class="[inputDisabled ? 'is-disabled' : '']" style="padding: 0 8px 0 8px">
          <div class="flex align-center" style="width: 70%">
            <img :src="getFileIconUrl(file?.name || '')" alt="" width="24" class="mr-4" />
            <span :title="file.name">
              {{ file.name }}
            </span>
          </div>
          <div class="flex align-center">
            <div :title="formatFileSize(file.size)">{{ formatFileSize(file.size) }}</div>

            <el-button link class="ml-8" @click="deleteFile(file)" v-if="!inputDisabled">
              <MkIcon name="icon_delete-trash_outlined"></MkIcon>
            </el-button>
          </div>
        </div>
      </el-card>
    </template>
  </el-space>
  <div class="mt-8 w-full" v-else>
    <div class="mb-8" v-if="downloadFiles.length">
      <el-space wrap class="w-full media-file-width upload_content">
        <template v-for="(item, index) in downloadFiles" :key="index">
          <el-card shadow="never" style="--el-card-padding: 8px" class="download-file cursor">
            <div class="download-button flex align-center" @click="downloadFile(item)">
              <el-icon class="mr-4">
                <Download />
              </el-icon>
              下载
            </div>
            <div class="show flex align-center">
              <img :src="getFileIconUrl(item?.name || '')" alt="" width="24" />
              <div class="ml-4" :title="item && item?.name">
                {{ item && item?.name }}
              </div>
            </div>
          </el-card>
        </template>
      </el-space>
    </div>
    <div class="mb-8" v-if="images.length">
      <el-space wrap>
        <template v-for="(item, index) in images" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <el-image
              :src="item.url"
              :zoom-rate="1.2"
              :max-scale="7"
              :min-scale="0.2"
              :preview-src-list="getAttrsArray(images, 'url')"
              :initial-index="index"
              alt=""
              fit="cover"
              style="width: 170px; height: 170px; display: block"
              class="border-r-6"
            />
          </div>
        </template>
      </el-space>
    </div>
    <div class="mb-8" v-if="audioFiles.length">
      <el-space wrap>
        <template v-for="(item, index) in audioFiles" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <audio :src="item.url" controls style="width: 350px; height: 43px" class="border-r-6" />
          </div>
        </template>
      </el-space>
    </div>
    <div class="mb-8" v-if="videoFiles.length">
      <el-space wrap>
        <template v-for="(item, index) in videoFiles" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <video :src="item.url" style="width: 170px; display: block" class="border-r-6" controls />
          </div>
        </template>
      </el-space>
    </div>
  </div>
</template>
<style lang="scss" scoped>
/* hover 显示下载按钮，样式照抄 question-content/index.vue */
.download-file {
  height: 43px;

  &:hover {
    color: var(--el-color-primary);
    border: 1px solid var(--el-color-primary);

    .download-button {
      display: block;
      text-align: center;
      line-height: 26px;
    }

    .show {
      display: none;
    }
  }

  .download-button {
    display: none;
  }
}

.upload_content {
  .is-disabled {
    background-color: var(--el-fill-color-light);
    color: var(--el-text-color-placeholder);
    cursor: not-allowed;
    &:hover {
      cursor: not-allowed;
    }
  }
  &.media-file-width {
    :deep(.el-space__item) {
      width: calc(50% - 4px) !important;
    }
  }
}
@media only screen and (max-width: 768px) {
  .upload_content {
    &.media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
  }
}
.debug-ai-chat {
  .upload_content {
    &.media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
  }
}
.execution-details {
  .upload_content {
    &.media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
  }
}
</style>
