<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { DocumentSplitResult, ImageDocumentImportPayload, ImageDocumentPreview } from '@/api/types'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import type { DragUploadFile, DragUploadHandler } from '@/components/mk-drag-upload/types'
import { getUploadValidationMessage } from '@/components/mk-drag-upload/validation'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import ImageProcessingForm from './ImageProcessingForm.vue'
import DocumentImportPreview from '../../document/components/DocumentImportPreview.vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'UploadImageDrawer' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['image']
  knowledgeId: string
  fileCountLimit?: number
  fileSizeLimit?: number
}>()
const emit = defineEmits<{ refresh: []; closed: [] }>()

/* 上传步骤暂存文件，处理步骤再按当前策略生成图片预览。 */
provide<DragUploadHandler>('upload', (file, onProgress) => FileApi.postUploadFile(file, undefined, FILE_SOURCE_TYPE.TEMPORARY_120_MINUTE, onProgress))
const visible = ref(false)
const loading = ref(false)
const activeStep = ref(0)
const processingMounted = ref(false)
const previewVisible = ref(false)
const previewDocuments = ref<(ImageDocumentPreview & DocumentSplitResult)[]>([])
const selectedFiles = ref<DragUploadFile[]>([])
const successfulFiles = computed(() => selectedFiles.value.filter((file) => file.status === 'success'))
const countLimit = computed(() => Math.min(50, props.fileCountLimit ?? 50))
const sizeLimit = computed(() => props.fileSizeLimit ?? 100)
const uploadRef = useTemplateRef<InstanceType<typeof MkDragUpload>>('uploadRef')
const processingRef = useTemplateRef<InstanceType<typeof ImageProcessingForm>>('processingRef')
const previewRef = useTemplateRef<InstanceType<typeof DocumentImportPreview>>('previewRef')
const uploading = computed(() => (uploadRef.value?.uploadingCount ?? 0) > 0)

function open() {
  visible.value = true
}

function validateFiles() {
  if (loading.value) return false
  const message = getUploadValidationMessage(selectedFiles.value)
  if (message) {
    MsgWarning(message)
    return false
  }
  return true
}

/* 步骤切换保留文件和处理策略；离开预览后重新生成，避免导入旧配置。 */
function handleNext() {
  if (!validateFiles()) return
  processingMounted.value = true
  activeStep.value = 1
}
function handlePrevious() {
  if (loading.value) return
  if (previewVisible.value) previewVisible.value = false
  else activeStep.value = 0
}

/* 图片预览：校验处理策略后请求预览，保留返回结果供导入。 */
function handleGeneratePreview() {
  if (!validateFiles() || !processingRef.value) return
  const fileIds = successfulFiles.value.flatMap((file) => (file.file_id ? [file.file_id] : []))
  if (fileIds.length !== successfulFiles.value.length) {
    MsgWarning('没有上传成功的文件，请重新上传')
    return
  }
  loading.value = true
  return processingRef.value
    .validate()
    .then((valid) => {
      if (!valid || !processingRef.value) return
      return props.api?.postUploadImagePreview(props.knowledgeId, fileIds, processingRef.value.getStrategy()).then((results) => {
        previewDocuments.value = results
        previewVisible.value = true
      })
    })
    .catch(() => {
      // 请求层统一提示错误，失败保留文件与策略。
    })
    .finally(() => {
      loading.value = false
    })
}

/* 图片导入：预览后提交生成结果的文件 ID，未预览直接提交上传成功的图片 ID。 */
async function handleSubmit() {
  if (!validateFiles() || (previewVisible.value && !previewRef.value?.validate())) return
  const fileIds = successfulFiles.value.flatMap((file) => (file.file_id ? [file.file_id] : []))
  if (!previewVisible.value && fileIds.length !== successfulFiles.value.length) {
    MsgWarning('没有上传成功的文件，请重新上传')
    return
  }

  loading.value = true
  try {
    if (!previewVisible.value) {
      const valid = await processingRef.value?.validate()
      if (!valid || !processingRef.value) return
    }
    const payload: ImageDocumentImportPayload = {
      file_id_list: previewVisible.value ? previewDocuments.value.map((preview) => preview.file_id) : fileIds,
    }
    if (!previewVisible.value) payload.doc_strategy = processingRef.value?.getStrategy()
    const importRequest = props.api?.putBatchCreateImageDocuments(props.knowledgeId, payload)
    if (!importRequest) return
    await importRequest
    MsgSuccess('导入成功')
    visible.value = false
    emit('refresh')
  } catch {
    // 请求层统一提示错误，失败保留文件、策略和预览供重试。
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" size="100%" :content-class="previewVisible ? 'h-full p-0!' : undefined" @closed="emit('closed')">
    <template #header>
      <div class="flex w-full">
        <h4>上传图片</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="上传图片" />
          <el-step title="图片处理" />
        </el-steps>
      </div>
    </template>
    <div class="h-full" v-loading="loading">
      <DocumentImportPreview v-if="previewVisible" ref="previewRef" v-model="previewDocuments" :knowledge-id="knowledgeId" />
      <div v-show="!previewVisible" class="mx-auto w-full max-w-200">
        <section v-show="activeStep === 0">
          <h4 class="mb-4 mk-title-decoration">上传图片</h4>
          <el-alert type="primary" :closable="false" show-icon class="mb-4!">
            <template #icon><MkIcon name="icon_info_filled" /></template>
            <ol class="list-inside list-decimal">
              <li>每次最多上传 {{ countLimit }} 个文件，每个文件不超过 {{ sizeLimit }} MB</li>
            </ol>
          </el-alert>
          <MkDragUpload
            ref="uploadRef"
            v-model="selectedFiles"
            multiple
            mode="image"
            accept=".jpg,.jpeg,.png,.webp,.bmp"
            :limit="countLimit"
            :size-limit="sizeLimit"
            tip-text="支持格式：JPG、JPEG、PNG、WEBP、BMP"
          />
        </section>
        <section v-if="processingMounted" v-show="activeStep === 1 && !previewVisible">
          <h4 class="mb-4 mk-title-decoration">图片处理</h4>
          <ImageProcessingForm ref="processingRef" />
        </section>
      </div>
    </div>
    <template #footer>
      <!-- 取消上传图片 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 返回上传步骤或图片处理设置 -->
      <el-button v-if="activeStep === 1" plain :disabled="loading" @click="handlePrevious">上一步</el-button>
      <!-- 进入图片处理步骤 -->
      <el-button v-if="activeStep === 0" type="primary" :disabled="loading || uploading" @click="handleNext">下一步</el-button>
      <!-- 按图片处理策略生成预览 -->
      <el-button v-if="activeStep === 1 && !previewVisible" plain :loading="loading" @click="handleGeneratePreview">生成预览</el-button>
      <!-- 导入处理后的图片 -->
      <el-button v-if="activeStep === 1" type="primary" :loading="loading" @click="handleSubmit">开始导入</el-button>
    </template>
  </MkDrawer>
</template>
