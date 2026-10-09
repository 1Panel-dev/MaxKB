<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { DragUploadFile, DragUploadHandler } from '@/components/mk-drag-upload/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentSplitResult } from '@/api/types'
import DocumentImportPreview from './DocumentImportPreview.vue'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { DOCUMENT_UPLOAD_OPTIONS, type DocumentUploadMode } from './constants'

defineOptions({ name: 'UploadDocumentDrawer' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  mode: DocumentUploadMode
  fileCountLimit?: number
  fileSizeLimit?: number
}>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
provide<DragUploadHandler>('upload', (file, onProgress) => FileApi.postUploadFile(file, undefined, FILE_SOURCE_TYPE.TEMPORARY_120_MINUTE, onProgress))

/* 文件选择与上传状态 */
const visible = ref(false)
const loading = ref(false)
const activeStep = ref(0)
const strategyMounted = ref(false)
const previewVisible = ref(false)
const previewDocuments = ref<DocumentSplitResult[]>([])
const uploadOption = computed(() => DOCUMENT_UPLOAD_OPTIONS[props.mode])
const countLimit = computed(() => Math.min(50, props.fileCountLimit ?? 50))
const sizeLimit = computed(() => props.fileSizeLimit ?? 100)
const selectedFiles = ref<DragUploadFile[]>([])
const uploadRef = useTemplateRef<InstanceType<typeof MkDragUpload>>('uploadRef')
const strategyRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyRef')
const previewRef = useTemplateRef<InstanceType<typeof DocumentImportPreview>>('previewRef')
const uploadComponentUploading = computed(() => (uploadRef.value?.uploadingCount ?? 0) > 0)
const successfulFiles = computed(() => selectedFiles.value.filter((file) => file.status === 'success'))

function open() {
  visible.value = true
}

/* 模板下载与文档导入 */
function handleDownloadTemplate(type: 'excel' | 'csv') {
  if (props.mode === 'text') return
  return props.mode === 'table' ? props.api.exportTableDocumentTemplate(type) : props.api.exportQADocumentTemplate(type)
}

function validateImportFiles() {
  if (loading.value || uploadComponentUploading.value) return false
  if (!successfulFiles.value.length) {
    MsgWarning('没有上传成功的文件，请重新上传')
    return false
  }
  return true
}

/* 下一步 */
function handleNext() {
  if (!validateImportFiles()) return
  strategyMounted.value = true
  activeStep.value = 1
}

/* 文本分段预览：解析结果保留策略与来源关联，编辑后直接用于导入。 */
function handleGeneratePreview() {
  if (!validateImportFiles() || !strategyRef.value) return
  loading.value = true
  return strategyRef.value
    .validate()
    .then((valid) => {
      if (!valid || !strategyRef.value) return
      const files = successfulFiles.value.flatMap((file) => (file.raw ? [file.raw] : []))
      return props.api.postSplitDocuments(props.knowledgeId, files, strategyRef.value.getStrategy()).then((documents) => {
        previewDocuments.value = documents
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

/* 上一步 */
function handlePrevious() {
  if (loading.value) return
  if (previewVisible.value) previewVisible.value = false
  else activeStep.value = 0
}

/* 文档导入 */
function handleSubmit() {
  if (!validateImportFiles()) return
  if (previewVisible.value && !previewRef.value?.validate()) return
  const files = successfulFiles.value.flatMap((file) => (file.raw ? [file.raw] : []))
  if (!files.length) return
  loading.value = true
  let importRequest: Promise<boolean>
  if (props.mode === 'table') {
    // 表格由服务端解析并创建文档。
    importRequest = props.api.postImportTableDocumentFiles(props.knowledgeId, files).then(() => true)
  } else if (props.mode === 'qa') {
    // QA 问答对由服务端解析并创建文档。
    importRequest = props.api.postImportQADocumentFiles(props.knowledgeId, files).then(() => true)
  } else if (previewVisible.value) {
    if (previewDocuments.value.every((document) => !document.content.length)) {
      MsgWarning('没有可导入的分段，请重新生成预览')
      loading.value = false
      return
    }
    importRequest = props.api
      .putBatchCreateDocuments(
        props.knowledgeId,
        previewDocuments.value.map(({ content, ...document }) => ({ ...document, paragraphs: content })),
      )
      .then(() => true)
  } else {
    // 文本校验处理策略，解析成功后批量创建文档。
    importRequest = Promise.resolve(strategyRef.value?.validate()).then((valid) => {
      if (!valid || !strategyRef.value) return false
      return props.api.postSplitDocuments(props.knowledgeId, files, strategyRef.value.getStrategy()).then((documents) => {
        return props.api
          .putBatchCreateDocuments(
            props.knowledgeId,
            documents.map(({ content, ...document }) => ({ ...document, paragraphs: content })),
          )
          .then(() => true)
      })
    })
  }
  return importRequest
    .then((success) => {
      if (!success) return
      MsgSuccess('导入成功')
      visible.value = false
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，失败保留文件与策略供重试。
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" size="100%" :content-class="previewVisible ? 'h-full p-0!' : undefined" @closed="emit('closed')">
    <template #header>
      <div class="flex w-full">
        <h4>{{ uploadOption.title }}</h4>
        <el-steps v-if="mode === 'text'" :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="上传文档" />
          <el-step title="文档处理策略" />
        </el-steps>
      </div>
    </template>

    <div class="h-full" v-loading="loading">
      <DocumentImportPreview v-if="previewVisible" ref="previewRef" v-model="previewDocuments" />
      <div v-show="!previewVisible" class="mx-auto w-full max-w-200">
        <section v-show="activeStep === 0">
          <h4 v-if="mode === 'text'" class="mb-4 mk-title-decoration">上传文档</h4>
          <el-alert type="primary" :closable="false" show-icon class="mb-4!">
            <template #icon><MkIcon name="icon_info_filled" /></template>

            <ol class="list-inside list-decimal space-y-1">
              <li v-if="mode === 'text'">文件上传前，建议规范文件的分段标识</li>
              <template v-else>
                <li>
                  <div class="inline-flex flex-wrap items-center gap-2">
                    <span>点击下载对应模板并完善信息：</span>
                    <!-- 下载 Excel 模板 -->
                    <el-button link type="primary" @click="handleDownloadTemplate('excel')">下载 Excel 模板</el-button>
                    <!-- 下载 CSV 模板 -->
                    <el-button link type="primary" @click="handleDownloadTemplate('csv')">下载 CSV 模板</el-button>
                  </div>
                </li>
                <li v-if="mode === 'table'">第一行必须是列标题，且列标题必须是有意义的术语，表中每条记录将作为一个分段</li>
                <li>上传的表格文件中每个 sheet 会作为一个文档，sheet 名称为文档名称</li>
              </template>
              <li>每次最多上传 {{ countLimit }} 个文件，每个文件不超过 {{ sizeLimit }} MB</li>
            </ol>
          </el-alert>
          <MkDragUpload
            ref="uploadRef"
            v-model="selectedFiles"
            multiple
            :accept="uploadOption.accept"
            :limit="countLimit"
            :size-limit="sizeLimit"
            :tip-text="`支持格式：${uploadOption.formats}`"
          ></MkDragUpload>
        </section>
        <section v-if="mode === 'text' && strategyMounted" v-show="activeStep === 1">
          <h4 class="mb-4 mk-title-decoration">文档处理策略</h4>
          <DocumentStrategyForm ref="strategyRef" />
        </section>
      </div>
    </div>

    <template #footer>
      <!-- 取消上传 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 返回上传步骤 -->
      <el-button v-if="activeStep === 1" plain :disabled="loading" @click="handlePrevious">上一步</el-button>
      <!-- 进入文档处理策略 -->
      <el-button v-if="mode === 'text' && activeStep === 0" type="primary" :disabled="loading || uploadComponentUploading" @click="handleNext">
        下一步
      </el-button>
      <!-- 生成文本分段预览 -->
      <el-button
        plain
        v-if="mode === 'text' && activeStep === 1 && !previewVisible"
        :loading="loading"
        :disabled="uploadComponentUploading"
        @click="handleGeneratePreview"
      >
        生成预览
      </el-button>
      <!-- 开始导入文档 -->
      <el-button
        v-if="mode !== 'text' || activeStep === 1"
        type="primary"
        :disabled="loading || uploadComponentUploading"
        :loading="loading"
        @click="handleSubmit"
      >
        开始导入
      </el-button>
    </template>
  </MkDrawer>
</template>
