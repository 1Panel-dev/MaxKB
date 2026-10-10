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

function handleDownloadTemplate() {
  if (loading.value || downloadLoading.value) return
  downloadLoading.value = true
  return props.api.exportKnowledgeTagTemplate(props.knowledgeId).finally(() => {
    downloadLoading.value = false
  })
}

function handleImport() {
  if (loading.value || downloadLoading.value) return
  importFormRef.value?.validate((valid) => {
    if (!valid || loading.value || downloadLoading.value) return
    const file = importForm.files[0]?.raw
    if (!file) {
      MsgWarning('请重新选择上传文件')
      return
    }

    loading.value = true
    return props.api
      .postImportKnowledgeTags(props.knowledgeId, file)
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
  <MkDialog v-model="visible" title="导入标签" @closed="resetData">
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
      <!-- 导入标签 -->
      <el-button type="primary" :loading="loading" :disabled="!importForm.files.length || downloadLoading" @click="handleImport">导入</el-button>
    </template>
  </MkDialog>
</template>
