<script setup lang="ts">
import { computed } from 'vue'
import type { UploadCardFile } from './types'

defineOptions({ name: 'ImageUploadCard' })
const props = withDefaults(
  defineProps<{
    file: UploadCardFile
    src?: string
    size?: number
    iconSize?: number
    percentage?: number
    disabled?: boolean
    showError?: boolean
    showRemove?: boolean
    previewSrcList?: string[]
    initialIndex?: number
  }>(),
  { size: 104, iconSize: 16, disabled: false, showError: true, showRemove: true, initialIndex: 0 },
)
const emit = defineEmits<{ retry: []; remove: [] }>()
const percentage = computed(() => props.percentage ?? props.file.percentage ?? 0)
</script>

<template>
  <div class="group relative shrink-0 overflow-hidden rounded-md" :style="{ width: `${size}px`, height: `${size}px` }">
    <!-- 查看图片，未提供预览列表时仅展示缩略图。 -->
    <el-image
      :src="src"
      :alt="file.name"
      :preview-src-list="previewSrcList"
      :initial-index="initialIndex"
      :scale="0.8"
      fit="cover"
      preview-teleported
      class="h-full w-full border"
      :class="{ 'border-danger!': file.status === 'fail' }"
    />
    <div v-if="file.status !== 'success'" class="pointer-events-none absolute inset-0 bg-N900/30" />
    <div v-if="file.status === 'ready' || file.status === 'uploading'" class="absolute-center w-3/5">
      <el-progress :percentage="file.status === 'uploading' ? percentage : 0" :stroke-width="4" :show-text="false" />
    </div>
    <div v-if="file.status === 'fail'" class="absolute-center flex-align-center gap-3">
      <MkTooltip v-if="showError" :content="`${file.name}：${file.errMsg}`" :disabled="!file.errMsg" placement="top" :offset="size / 2">
        <span class="flex-center"><MkIcon name="icon_warning_filled" class="text-danger!" :size="iconSize" /></span>
      </MkTooltip>
      <!-- 重新上传失败图片 -->
      <MkTooltip content="重新上传" placement="top" :offset="size / 2">
        <button type="button" class="flex-center cursor-pointer disabled:cursor-not-allowed" :disabled="disabled" @click.stop="emit('retry')">
          <MkIcon name="icon_refresh_outlined" class="text-white!" :size="iconSize" />
        </button>
      </MkTooltip>
    </div>
    <!-- 删除已选图片 -->
    <button
      v-if="showRemove"
      type="button"
      class="group-hover-visible mk-remove-button disabled:cursor-not-allowed"
      title="删除图片"
      :disabled="disabled"
      @click.stop="emit('remove')"
    >
      <MkIcon name="icon_close_bold_outlined" class="text-white!" :size="6" />
    </button>
  </div>
</template>
