<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { KnowledgeHitTestImage, KnowledgeHitTestPayload } from '@/api/types'
import { KNOWLEDGE_IMAGE_EXTENSIONS, KNOWLEDGE_IMAGE_ACCEPT, KNOWLEDGE_IMAGE_TYPE_LABEL } from '@/constants/knowledge'
import { MsgWarning } from '@/utils/message'
import { useInputEvents } from '@/conversation-panel/core/input-events'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'

defineOptions({ name: 'KnowledgeHitTestInput' })

const props = withDefaults(
  defineProps<{
    loading?: boolean
    allowImages?: boolean
    fileCountLimit?: number
    fileSizeLimit?: number
  }>(),
  { loading: false, allowImages: true },
)
const emit = defineEmits<{
  submit: [query: Required<Pick<KnowledgeHitTestPayload, 'query_text' | 'image_list'>>]
}>()

interface QueryImage {
  id: number
  name: string
  raw: File
  previewUrl: string
  status: 'ready' | 'uploading' | 'success' | 'fail'
  percentage: number
  errMsg?: string
  uploadedImage?: KnowledgeHitTestImage
}

// 查询图片先上传为临时文件，仅将上传成功的引用交给召回接口。
const countLimit = computed(() => Math.min(50, props.fileCountLimit ?? 50))
const sizeLimit = computed(() => props.fileSizeLimit ?? 100)
const queryText = ref('')
const queryImages = ref<QueryImage[]>([])
const uploadRequests = new Map<number, () => void>()
const hasImages = computed(() => queryImages.value.length > 0)
const canSelectImages = computed(() => props.allowImages && !props.loading && queryImages.value.length < countLimit.value)
const canSubmit = computed(
  () =>
    !props.loading &&
    (!!queryText.value.trim() || hasImages.value) &&
    queryImages.value.every((image) => image.status === 'success' && image.uploadedImage),
)
let nextImageId = 0

// 文本和附件入口与对话输入保持一致，具体上传限制由知识库配置决定。
const { fileInputRef, handleFileSelect, handlePaste, handleDragover, handleDrop, handleKeydown } = useInputEvents({
  text: queryText,
  canUpload: () => canSelectImages.value,
  addFiles: addImages,
  submit: submitTest,
})

function submitTest() {
  if (!canSubmit.value) return
  emit('submit', {
    query_text: queryText.value.trim(),
    image_list: queryImages.value.flatMap((image) => (image.uploadedImage ? [{ ...image.uploadedImage }] : [])),
  })
}

// 图片格式和大小校验，失败文件不加入查询列表。
function validateImage(file: File) {
  const filename = file.name.toUpperCase()
  if (!KNOWLEDGE_IMAGE_EXTENSIONS.some((extension) => filename.endsWith(`.${extension}`))) {
    MsgWarning('文件格式不支持')
    return false
  }
  if (!file.size || file.size > sizeLimit.value * 1024 * 1024) {
    MsgWarning(file.size ? '大小超限' : '文件不能为空')
    return false
  }
  return true
}

// 所有附件入口统一校验后创建缩略图，再开始上传。
function addImages(files: FileList | File[]) {
  if (!canSelectImages.value) return

  for (const file of Array.from(files)) {
    if (queryImages.value.length >= countLimit.value) {
      MsgWarning(`每次最多上传 ${countLimit.value} 个文件`)
      break
    }
    if (!validateImage(file)) continue

    const image = reactive<QueryImage>({
      id: ++nextImageId,
      name: file.name,
      raw: file,
      previewUrl: URL.createObjectURL(file),
      status: 'ready',
      percentage: 0,
    })
    queryImages.value.push(image)
    uploadImage(image)
  }
}

function uploadImage(image: QueryImage) {
  if (props.loading || image.status === 'uploading' || uploadRequests.has(image.id) || !queryImages.value.includes(image)) return
  image.status = 'uploading'
  image.percentage = 0
  image.errMsg = ''
  // Promise 链覆盖同步抛错和请求失败，取消时重置状态以忽略后续回调。
  void Promise.resolve()
    .then(() => {
      if (image.status !== 'uploading') return
      const { request, abort } = FileApi.postUploadFile(image.raw, undefined, FILE_SOURCE_TYPE.TEMPORARY_120_MINUTE, (percentage) => {
        if (image.status !== 'uploading') return
        image.percentage = Number.isFinite(percentage) ? Math.min(100, Math.max(0, percentage)) : 0
      })
      uploadRequests.set(image.id, abort)
      return request.then((url) => {
        if (image.status !== 'uploading') return
        const fileId = url.split(/[?#]/)[0]?.split('/').filter(Boolean).pop()
        if (!fileId) throw new Error('上传图片未返回文件 ID')
        image.uploadedImage = { file_id: fileId, name: image.name, url }
        image.percentage = 100
        image.status = 'success'
      })
    })
    .catch(() => {
      // 保留原文件和缩略图，供重试或移除。
      if (image.status !== 'uploading') return
      image.status = 'fail'
      image.errMsg = '上传失败'
    })
    .finally(() => uploadRequests.delete(image.id))
}

function retryImage(image: QueryImage) {
  if (image.status === 'fail' && validateImage(image.raw)) uploadImage(image)
}

function cancelUpload(image: QueryImage) {
  if (image.status === 'uploading') image.status = 'ready'
  uploadRequests.get(image.id)?.()
  uploadRequests.delete(image.id)
}

function removeImage(image: QueryImage) {
  if (props.loading) return
  cancelUpload(image)
  queryImages.value = queryImages.value.filter((queryImage) => queryImage.id !== image.id)
  URL.revokeObjectURL(image.previewUrl)
}

// 只取消尚未完成的上传，已上传临时文件由服务端按有效期清理。
onBeforeUnmount(() => {
  for (const image of queryImages.value) {
    cancelUpload(image)
    URL.revokeObjectURL(image.previewUrl)
  }
})
</script>

<template>
  <div
    class="mk-input-box min-h-20 border transition-colors hover:border-primary focus-within:border-primary"
    @dragover="handleDragover"
    @drop="handleDrop"
    @paste="handlePaste"
  >
    <MkHorizontalScroll v-if="queryImages.length" class="mb-3">
      <template v-for="image in queryImages" :key="image.id">
        <!-- 重试或移除查询图片 -->
        <ImageUploadCard
          :file="image"
          :src="image.previewUrl"
          :size="58"
          :disabled="loading"
          @retry="retryImage(image)"
          @remove="removeImage(image)"
        />
      </template>
    </MkHorizontalScroll>

    <!-- 输入召回测试内容 -->
    <el-input
      v-model="queryText"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 7 }"
      resize="none"
      placeholder="请输入测试内容"
      :maxlength="100000"
      @keydown.enter="handleKeydown"
    />
    <div v-if="allowImages" class="text-right mt-3">
      <input
        ref="fileInputRef"
        type="file"
        multiple
        :accept="KNOWLEDGE_IMAGE_ACCEPT"
        :disabled="!canSelectImages"
        class="hidden"
        @change="handleFileSelect"
      />

      <MkTooltip placement="top">
        <template #content>
          <div class="break-all whitespace-pre-wrap">
            可拖拽到输入框内上传图片
            <br />
            上传图片：最多{{ countLimit }}张，每张不超过 {{ sizeLimit }}MB
            <br />
            图片类型：{{ KNOWLEDGE_IMAGE_TYPE_LABEL }}
          </div>
        </template>
        <!-- 上传图片 -->
        <el-button text :disabled="!canSelectImages" @click="fileInputRef?.click()">
          <MkIcon name="icon_attachment_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </div>
  </div>
  <!-- 执行召回测试 -->
  <el-button type="primary" class="mt-4 w-full" :loading="loading" :disabled="!canSubmit" @click="submitTest">
    <MkIcon name="icon_play_outlined" />
    <span>测试</span>
  </el-button>
</template>
