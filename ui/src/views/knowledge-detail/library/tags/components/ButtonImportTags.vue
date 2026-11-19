<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ButtonImportTags' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ knowledgeId: string; api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['tags']; disabled?: boolean }>()
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
const rules = computed<FormRules<ImportTagsForm>>(() => ({
  files: [{ required: true, type: 'array', min: 1, message: t('upload.requiredMessage'), trigger: 'change' }],
}))

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
    MsgWarning(t('knowledge.tags.import.unsupportedFormatMessage'))
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
  return (props.api.exportKnowledgeTagTemplate?.(props.knowledgeId) ?? Promise.resolve()).finally(() => {
    downloadLoading.value = false
  })
}

function handleImport() {
  if (loading.value || downloadLoading.value) return
  importFormRef.value?.validate((valid) => {
    if (!valid || loading.value || downloadLoading.value) return
    const file = importForm.files[0]?.raw
    if (!file) {
      MsgWarning(t('upload.reselectFileMessage'))
      return
    }

    loading.value = true
    return (
      props.api.postImportKnowledgeTags?.(props.knowledgeId, file).then(() => {
        MsgSuccess(t('common.messages.importSuccess'))
        visible.value = false
        emit('refresh')
      }) ?? Promise.resolve()
    ).finally(() => {
      loading.value = false
    })
  })
}
</script>

<template>
  <!-- 打开标签导入弹窗 -->
  <el-button plain :disabled="disabled" @click="handleOpenDialog">
    <MkIcon name="icon_import_outlined" />
    <span>{{ t('common.actions.import') }}</span>
  </el-button>
  <MkDialog v-model="visible" :title="t('knowledge.tags.import.title')" @closed="resetData">
    <el-form
      ref="importFormRef"
      v-loading="loading"
      :model="importForm"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item prop="files" class="mk-hide-asterisk">
        <template #label>
          <div class="flex-between w-full">
            <span class="mk-required">{{ t('common.actions.uploadFiles') }}</span>
            <!-- 下载标签导入模板 -->
            <el-button link type="primary" :loading="downloadLoading" :disabled="loading" @click="handleDownloadTemplate">
              {{ t('knowledge.tags.import.downloadTemplate') }}
            </el-button>
          </div>
        </template>
        <MkDragUpload
          ref="dragUploadRef"
          v-model="importForm.files"
          accept=".xls,.xlsx"
          :tip-text="`${t('upload.formats')}: ${['XLS', 'XLSX'].join('、')}`"
          @change="handleFileChange"
          @remove="handleFileRemove"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消标签导入 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 导入标签 -->
      <el-button type="primary" :loading="loading" :disabled="!importForm.files.length" @click="handleImport">
        {{ t('common.actions.import') }}
      </el-button>
    </template>
  </MkDialog>
</template>
