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
    <el-button type="primary">{{ $t('chat.uploadFile.label') }}</el-button>
  </el-upload>
  <el-space wrap class="w-full media-file-width upload_content mt-16">
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
</template>
<script setup lang="ts">
import { computed, inject, ref, useAttrs } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormField } from '@/components/dynamics-form/type'
import { getImgUrl } from '@/utils/common'
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

const loading = ref<boolean>(false)

const uploadFile = async (file: any, fileList: Array<any>) => {
  fileList.splice(fileList.indexOf(file), 1)
  if (fileArray.value.find((f: any) => f.name === file.name)) {
    ElMessage.warning(t('chat.uploadFile.fileRepeat'))

    return
  }
  const max_file_size = (props.formField as any).max_file_size
  if (file.size / 1024 / 1024 > max_file_size) {
    ElMessage.warning(t('chat.uploadFile.sizeLimit') + max_file_size + 'MB')
    return
  }

  if (fileList.length > attrs.limit) {
    ElMessage.warning(
      t('chat.uploadFile.limitMessage1') + attrs.limit + t('chat.uploadFile.limitMessage2'),
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
