<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import type TagsApi from '@/api/admin/workspace/knowledge/tags'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ButtonImportTags' })

const props = defineProps<{ knowledgeId: string; api: typeof TagsApi; disabled?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()

interface ImportTagsForm {
  files: UploadUserFile[]
}

const visible = ref(false)
const loading = ref(false)
const downloadLoading = ref(false)
const importFormRef = ref<FormInstance>()
const dragUploadRef = ref<InstanceType<typeof MkDragUpload>>()
const importForm = reactive<ImportTagsForm>({ files: [] })
const rules: FormRules<ImportTagsForm> = {
  files: [{ required: true, type: 'array', min: 1, message: '请上传文件', trigger: 'change' }],
}

/* 导入入口与关闭清理。 */
function handleOpenDialog() {
  if (props.disabled) return
  visible.value = true
}

function resetData() {
  importForm.files = []
  loading.value = false
  downloadLoading.value = false
  dragUploadRef.value?.clearFiles()
  importFormRef.value?.clearValidate()
}

/* 文件只在本地暂存，替换时保留最新选择的一个文件。 */
function handleFileChange(file: UploadFile) {
  if (!/\.xlsx?$/i.test(file.name)) {
    importForm.files = []
    dragUploadRef.value?.clearFiles()
    MsgWarning('仅支持上传 XLS、XLSX 格式的文件')
    return
  }

  importForm.files = [file]
  nextTick(() => importFormRef.value?.validateField('files'))
}

function handleFileRemove() {
  importForm.files = []
  nextTick(() => importFormRef.value?.validateField('files'))
}

function requestDownloadTemplate(): Promise<unknown> | undefined {
  // TODO：接入 props.api 的标签模板下载请求，复用请求层文件下载能力并返回 Promise。
  return undefined
}

function handleDownloadTemplate() {
  if (loading.value || downloadLoading.value) return
  const request = requestDownloadTemplate()
  if (!request) {
    MsgWarning('标签模板下载接口尚未接入')
    return
  }

  downloadLoading.value = true
  return request.finally(() => {
    downloadLoading.value = false
  })
}

function requestImportTags(): Promise<unknown> | undefined {
  // TODO：接入 props.api 的标签导入请求，传入 props.knowledgeId、importForm.files[0].raw 并返回 Promise。
  // 成功关闭和刷新已处理，失败应 reject。
  return undefined
}

function handleImport() {
  if (loading.value || downloadLoading.value) return
  importFormRef.value?.validate((valid) => {
    if (!valid || loading.value || downloadLoading.value) return
    const request = requestImportTags()
    if (!request) {
      MsgWarning('标签导入接口尚未接入，当前文件尚未上传')
      return
    }

    loading.value = true
    return request
      .then(() => {
        MsgSuccess('导入成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}
</script>

<template>
  <!-- 打开标签导入弹窗 -->
  <el-button plain :disabled="disabled" @click="handleOpenDialog">
    <MkIcon name="icon_import_outlined" />
    <span>导入</span>
  </el-button>
  <MkDialog v-model="visible" title="导入标签" :show-close="!loading && !downloadLoading" @closed="resetData">
    <el-form ref="importFormRef" v-loading="loading" :model="importForm" :rules="rules" label-position="top" @submit.prevent>
      <el-form-item prop="files" :required="false">
        <template #label>
          <div class="flex-between w-full">
            <span>
              上传文件
              <span class="ml-1 text-danger">*</span>
            </span>
            <!-- 下载标签导入模板 -->
            <el-button link type="primary" :loading="downloadLoading" :disabled="loading" @click="handleDownloadTemplate">下载模板</el-button>
          </div>
        </template>
        <MkDragUpload
          ref="dragUploadRef"
          v-model="importForm.files"
          accept=".xls,.xlsx"
          tip-text="支持格式：XLS、XLSX"
          @change="handleFileChange"
          @remove="handleFileRemove"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消标签导入 -->
      <el-button plain :disabled="loading || downloadLoading" @click="visible = false">取消</el-button>
      <!-- 导入标签，接口待接入 -->
      <el-button type="primary" :loading="loading" :disabled="!importForm.files.length || downloadLoading" @click="handleImport">导入</el-button>
    </template>
  </MkDialog>
</template>
