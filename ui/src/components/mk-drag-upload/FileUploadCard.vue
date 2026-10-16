<script setup lang="ts">
import { computed } from 'vue'
import { getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import type { UploadCardFile } from './types'

defineOptions({ name: 'FileUploadCard' })
const props = withDefaults(
  defineProps<{ file: UploadCardFile; description?: string; percentage?: number; disabled?: boolean; showRemove?: boolean }>(),
  {
    disabled: false,
    showRemove: true,
  },
)
const emit = defineEmits<{ retry: []; remove: [] }>()
defineSlots<{
  name?: (props: { file: UploadCardFile }) => unknown
  description?: (props: { file: UploadCardFile; percentage: number }) => unknown
}>()

const percentage = computed(() => props.percentage ?? props.file.percentage ?? 0)
</script>

<template>
  <el-card shadow="never" class="small relative overflow-hidden!" :class="{ 'border-danger!': file.status === 'fail' }">
    <div class="flex-align-center gap-3">
      <img :src="getFileIconUrl(file.name)" alt="" class="size-8 shrink-0" />
      <div class="min-w-0 flex-1">
        <slot name="name" :file="file">
          <p class="truncate" :title="file.name">{{ file.name }}</p>
        </slot>
        <div class="flex-align-center gap-2 text-sm">
          <span class="min-w-0 text-N500">
            <slot name="description" :file="file" :percentage="percentage">
              <template v-if="description !== undefined">{{ description }}</template>
              <template v-else>
                <template v-if="file.status === 'uploading'">{{ formatFileSize(((file.size ?? 0) * percentage) / 100) }} /</template>
                {{ formatFileSize(file.size) }}
              </template>
            </slot>
          </span>
          <span v-if="file.status === 'fail'" class="truncate text-danger" :title="file.errMsg">{{ file.errMsg }}</span>
        </div>
      </div>
      <div v-if="showRemove || file.status === 'fail'" class="flex shrink-0 gap-1">
        <!-- 重新上传失败附件 -->
        <el-button v-if="file.status === 'fail'" :disabled="disabled" text title="重新上传" @click.stop="emit('retry')">
          <MkIcon name="icon_refresh_outlined" />
        </el-button>
        <!-- 删除已选附件 -->
        <el-button v-if="showRemove" :disabled="disabled" text title="删除文件" @click.stop="emit('remove')">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </div>
    </div>
    <el-progress
      v-if="file.status === 'uploading'"
      :percentage="percentage"
      :stroke-width="4"
      :show-text="false"
      class="absolute! inset-x-0 bottom-0"
    />
  </el-card>
</template>
