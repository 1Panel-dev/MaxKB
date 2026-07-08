<template>
  <el-upload
    style="width: 100%"
    v-loading="loading"
    action="#"
    v-bind="$attrs"
    :auto-upload="false"
    :on-change="(file: any, fileList: any) => uploadFile(file, fileList)"
    v-model:file-list="model_value"
    multiple
    :show-file-list="false"
  >
    <el-button type="primary">{{ $t('aiChat.uploadFile.label') }}</el-button>
  </el-upload>
  <el-space wrap class="w-full media-file-width upload_content mt-16" v-if="!inputDisabled">
    <template v-for="(file, index) in model_value" :key="index">
      <el-card style="--el-card-padding: 0" shadow="never">
        <div
          class="flex-between"
          :class="[inputDisabled ? 'is-disabled' : '']"
          style="padding: 0 8px 0 8px"
        >
          <div class="flex align-center" style="width: 70%">
            <img :src="getImgUrl(file && file?.name)" alt="" width="24" class="mr-4" />
            <span class="ellipsis-1" :title="file.name">
              {{ file.name }}
            </span>
          </div>
          <div class="flex align-center">
            <div class="ellipsis-1" :title="formatSize(file.size)">{{ formatSize(file.size) }}</div>

            <el-button link class="ml-8" @click="deleteFile(file)" v-if="!inputDisabled">
              <AppIcon iconName="app-delete"></AppIcon>
            </el-button>
          </div>
        </div>
      </el-card>
    </template>
  </el-space>
  <div class="mt-8 w-full" v-else>
    <div class="mb-8" v-if="download_list.length">
      <el-space wrap class="w-full media-file-width upload_content">
        <template v-for="(item, index) in download_list" :key="index">
          <el-card shadow="never" style="--el-card-padding: 8px" class="download-file cursor">
            <div class="download-button flex align-center" @click="downloadFile(item)">
              <el-icon class="mr-4">
                <Download />
              </el-icon>
              {{ $t('aiChat.download') }}
            </div>
            <div class="show flex align-center">
              <img :src="getImgUrl(item && item?.name)" alt="" width="24" />
              <div class="ml-4 ellipsis-1" :title="item && item?.name">
                {{ item && item?.name }}
              </div>
            </div>
          </el-card>
        </template>
      </el-space>
    </div>
    <div class="mb-8" v-if="image_list.length">
      <el-space wrap>
        <template v-for="(item, index) in image_list" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <el-image
              :src="item.url"
              :zoom-rate="1.2"
              :max-scale="7"
              :min-scale="0.2"
              :preview-src-list="getAttrsArray(image_list, 'url')"
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
    <div class="mb-8" v-if="audio_list.length">
      <el-space wrap>
        <template v-for="(item, index) in audio_list" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <audio :src="item.url" controls style="width: 350px; height: 43px" class="border-r-6" />
          </div>
        </template>
      </el-space>
    </div>
    <div class="mb-8" v-if="video_list.length">
      <el-space wrap>
        <template v-for="(item, index) in video_list" :key="index">
          <div class="file cursor border-r-6" v-if="item.url">
            <video :src="item.url" style="width: 170px; display: block" class="border-r-6" controls />
          </div>
        </template>
      </el-space>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, inject, ref, useAttrs } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormField } from '@/components/dynamics-form/type'
import { getImgUrl, downloadByURL, getFileUrl, fileType } from '@/utils/common'
import { getAttrsArray } from '@/utils/array'
import { t } from '@/locales'
import { useFormDisabled } from 'element-plus'
const inputDisabled = useFormDisabled()
const attrs = useAttrs() as any
const upload = inject('upload') as any
const props = withDefaults(defineProps<{ modelValue?: any; formField: FormField }>(), {
  modelValue: () => [],
})
const emit = defineEmits(['update:modelValue'])
function formatSize(sizeInBytes: number) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = sizeInBytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return size.toFixed(2) + ' ' + units[unitIndex]
}

const deleteFile = (file: any) => {
  if (inputDisabled.value) {
    return
  }
  fileArray.value = fileArray.value.filter((f: any) => f.uid != file.uid)
  emit('update:modelValue', fileArray.value)
}

const model_value = computed({
  get: () => {
    if (!props.modelValue) {
      emit('update:modelValue', [])
    }
    return props.modelValue
  },
  set: (v: Array<any>) => {
    emit('update:modelValue', v)
  },
})
const fileArray = ref<any>([])

const imageExtensions = ['JPG', 'JPEG', 'PNG', 'GIF', 'BMP']
const videoExtensions = ['MP4', 'AVI', 'MKV', 'MOV', 'FLV', 'WMV']
const audioExtensions = ['MP3', 'WAV', 'OGG', 'AAC', 'M4A']
const ofType = (exts: string[]) => (f: any) => exts.includes(fileType(f?.name || '').toUpperCase())

const files_with_url = computed(() =>
  (model_value.value || []).map((f: any) => ({ ...f, url: f.url || getFileUrl(f.file_id) })),
)
const image_list = computed(() => files_with_url.value.filter(ofType(imageExtensions)))
const audio_list = computed(() => files_with_url.value.filter(ofType(audioExtensions)))
const video_list = computed(() => files_with_url.value.filter(ofType(videoExtensions)))
// 非图片/音频/视频的（文档、压缩包等）统一走下载卡片
const download_list = computed(() =>
  files_with_url.value.filter(
    (f: any) => !ofType([...imageExtensions, ...audioExtensions, ...videoExtensions])(f),
  ),
)

function downloadFile(item: any) {
  downloadByURL(item.url, item.name)
}

const loading = ref<boolean>(false)

const uploadFile = async (file: any, fileList: Array<any>) => {
  fileList.splice(fileList.indexOf(file), 1)
  if (fileArray.value.find((f: any) => f.name === file.name)) {
    ElMessage.warning(t('aiChat.uploadFile.fileRepeat'))

    return
  }
  const max_file_size = (props.formField as any).max_file_size
  if (file.size / 1024 / 1024 > max_file_size) {
    ElMessage.warning(t('aiChat.uploadFile.sizeLimit') + max_file_size + 'MB')
    return
  }

  if (fileList.length > attrs.limit) {
    ElMessage.warning(
      t('aiChat.uploadFile.limitMessage1') + attrs.limit + t('aiChat.uploadFile.limitMessage2'),
    )
    return
  }
  upload(file.raw, loading).then((ok: any) => {
    const split_path = ok.data.split('/')
    const file_id = split_path[split_path.length - 1]
    fileArray.value?.push({ name: file.name, file_id, size: file.size })
    emit('update:modelValue', fileArray.value)
  })
}
</script>
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
