<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { KnowledgeHitTestImage } from '@/api/types'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'KnowledgeHitTestInput' })

const props = withDefaults(defineProps<{ modelValue: string; disabled?: boolean; allowImages?: boolean }>(), { disabled: false, allowImages: true })
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:images': [images: KnowledgeHitTestImage[]]
  'update:uploading': [uploading: boolean]
  'update:failed': [failed: boolean]
}>()

interface QueryImage {
  id: number
  name: string
  previewUrl: string
  status: 'uploading' | 'success' | 'failed'
  uploadedImage?: KnowledgeHitTestImage
}

// 查询图片先上传为临时文件，仅将上传成功的引用交给召回接口。
const maxImageCount = 10
const maxImageSizeMB = 20
const imageInputRef = ref<HTMLInputElement>()
const queryImages = ref<QueryImage[]>([])
const uploadRequests = new Map<number, () => void>()
const canSelectImages = computed(() => props.allowImages && !props.disabled && queryImages.value.length < maxImageCount)
const hasFailedImages = computed(() => queryImages.value.some((image) => image.status === 'failed'))
let nextImageId = 0
let disposed = false

watch(
  () => queryImages.value.flatMap((image) => (image.uploadedImage ? [image.uploadedImage] : [])),
  (images) => emit('update:images', images),
  { immediate: true, flush: 'sync' },
)
watch(
  () => queryImages.value.some((image) => image.status === 'uploading'),
  (uploading) => emit('update:uploading', uploading),
  { immediate: true, flush: 'sync' },
)
watch(hasFailedImages, (failed) => emit('update:failed', failed), { immediate: true })

function selectImages(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  input.value = ''
  if (!canSelectImages.value) return

  for (const file of files) {
    if (queryImages.value.length >= maxImageCount) {
      MsgWarning(`每次最多上传 ${maxImageCount} 张图片`)
      break
    }
    if (!/\.(jpe?g|png|gif|webp)$/i.test(file.name)) {
      MsgWarning('仅支持 JPG、PNG、GIF、WebP 图片')
      continue
    }
    if (!file.size || file.size > maxImageSizeMB * 1024 * 1024) {
      MsgWarning(file.size ? `每张图片不能超过 ${maxImageSizeMB}MB` : '图片不能为空')
      continue
    }

    const image = reactive<QueryImage>({
      id: ++nextImageId,
      name: file.name,
      previewUrl: URL.createObjectURL(file),
      status: 'uploading',
    })
    queryImages.value.push(image)
    uploadImage(image, file)
  }
}

function uploadImage(image: QueryImage, file: File) {
  // 上传返回资源地址，末段是召回接口要求的 file_id。
  void Promise.resolve()
    .then(() => {
      if (disposed || !queryImages.value.includes(image)) return
      const { request, abort } = FileApi.postUploadFile(file, undefined, FILE_SOURCE_TYPE.TEMPORARY_120_MINUTE)
      uploadRequests.set(image.id, abort)
      return request.then((url) => {
        if (disposed || !queryImages.value.includes(image)) return
        const fileId = url.split(/[?#]/)[0]?.split('/').filter(Boolean).pop()
        if (!fileId) throw new Error('上传图片未返回文件 ID')
        image.uploadedImage = { file_id: fileId, name: file.name, url }
        image.status = 'success'
      })
    })
    .catch(() => {
      // 请求层提示上传错误，保留缩略图供移除后重新选择。
      if (!disposed && queryImages.value.includes(image)) image.status = 'failed'
    })
    .finally(() => uploadRequests.delete(image.id))
}

function removeImage(image: QueryImage) {
  if (props.disabled) return
  queryImages.value = queryImages.value.filter((queryImage) => queryImage.id !== image.id)
  uploadRequests.get(image.id)?.()
  uploadRequests.delete(image.id)
  URL.revokeObjectURL(image.previewUrl)
}

// 只取消尚未完成的上传，已上传临时文件由服务端按有效期清理。
onBeforeUnmount(() => {
  disposed = true
  for (const abort of uploadRequests.values()) abort()
  for (const image of queryImages.value) URL.revokeObjectURL(image.previewUrl)
  uploadRequests.clear()
})
</script>

<template>
  <div class="mk-input-box border" :class="{ 'bg-N100!': disabled }">
    <MkHorizontalScroll v-if="queryImages.length" class="mb-3">
      <template v-for="image in queryImages" :key="image.id">
        <div class="group relative shrink-0">
          <!-- 预览查询图片 -->
          <el-image
            :src="image.previewUrl"
            :alt="image.name"
            :title="image.name"
            :preview-src-list="[image.previewUrl]"
            :scale="0.8"
            preview-teleported
            fit="cover"
            class="size-20 rounded-lg border"
          />
          <div v-if="image.status === 'uploading'" class="pointer-events-none absolute inset-0 flex-center rounded-lg bg-N900/30">
            <LoadingIcon :size="20" class="text-white" />
          </div>
          <div
            v-else-if="image.status === 'failed'"
            class="pointer-events-none absolute inset-x-0 bottom-0 rounded-b-lg bg-danger/90 py-1 text-center text-sm text-white"
          >
            上传失败
          </div>
          <!-- 移除查询图片 -->
          <button
            type="button"
            class="mk-remove-button group-hover-visible disabled:cursor-not-allowed"
            title="移除图片"
            :disabled="disabled"
            @click="removeImage(image)"
          >
            <MkIcon name="icon_close_bold_outlined" :size="8" class="text-white!" />
          </button>
        </div>
      </template>
    </MkHorizontalScroll>
    <p v-if="hasFailedImages" class="mb-2 text-sm text-danger">请移除上传失败的图片后再测试</p>

    <!-- 输入召回测试内容 -->
    <el-input
      :model-value="modelValue"
      type="textarea"
      :autosize="{ minRows: 2, maxRows: 7 }"
      resize="none"
      placeholder="请输入测试内容"
      :disabled="disabled"
      @update:model-value="emit('update:modelValue', $event)"
    />
    <div class="mt-2 flex min-h-8 justify-end">
      <input
        ref="imageInputRef"
        type="file"
        multiple
        accept=".jpg,.jpeg,.png,.gif,.webp"
        :disabled="!canSelectImages"
        class="hidden"
        @change="selectImages"
      />
      <MkTooltip v-if="allowImages" :content="`最多 ${maxImageCount} 张图片，每张不超过 ${maxImageSizeMB}MB，支持 JPG、PNG、GIF、WebP`">
        <!-- 上传查询图片 -->
        <el-button text :disabled="!canSelectImages" title="上传图片" @click="imageInputRef?.click()">
          <MkIcon :icon="Picture" :size="20" />
        </el-button>
      </MkTooltip>
    </div>
  </div>
</template>
