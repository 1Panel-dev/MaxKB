<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentItem, KnowledgeItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'ParagraphMigrateDialog' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
}>()
const emit = defineEmits<{ success: [paragraphIds: string[]]; closed: [] }>()

// 固定本次勾选的分段，查询知识库与联动文档选项。
const visible = ref(false)
const migrationSucceeded = ref(false)
const loading = ref(false)
const knowledgeLoading = ref(false)
const documentLoading = ref(false)
const optionLoading = computed(() => knowledgeLoading.value || documentLoading.value)
const targetParagraphIds = ref<string[]>([])
const knowledgeOptions = ref<KnowledgeItem[]>([])
const documentOptions = ref<DocumentItem[]>([])
const knowledgeById = computed(() => new Map(knowledgeOptions.value.map((knowledge) => [knowledge.id, knowledge])))
const formRef = useTemplateRef<FormInstance>('formRef')
const migrateForm = reactive({ knowledge_id: '', document_id: '' })
const rules: FormRules<typeof migrateForm> = {
  knowledge_id: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  document_id: [{ required: true, message: '请选择文档', trigger: 'change' }],
}

function open(paragraphIds: string[]) {
  if (visible.value || loading.value || optionLoading.value || !paragraphIds.length) return
  targetParagraphIds.value = [...paragraphIds]
  visible.value = true
  knowledgeLoading.value = true
  return KnowledgeApi.getAllKnowledge()
    .then((knowledge) => {
      knowledgeOptions.value = knowledge
    })
    .catch(() => {
      // 请求层统一提示错误。
    })
    .finally(() => {
      knowledgeLoading.value = false
    })
}

function handleKnowledgeChange(knowledgeId: string) {
  migrateForm.document_id = ''
  documentOptions.value = []
  formRef.value?.clearValidate('document_id')
  if (!knowledgeId) return
  documentLoading.value = true
  return DocumentApi.getAllDocuments(knowledgeId)
    .then((documents) => {
      documentOptions.value = documents.filter(({ id }) => id !== props.documentId)
    })
    .catch(() => {
      // 请求层统一提示错误，文档保持空选。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

// 迁移成功后关闭并通知页面移除本次分段，失败保留当前选择以便重试。
async function handleSubmit() {
  if (loading.value || optionLoading.value || !targetParagraphIds.value.length) return
  if (!(await formRef.value?.validate().catch(() => false)) || loading.value) return
  loading.value = true
  return props.api
    .putMigrateParagraphs(props.knowledgeId, props.documentId, migrateForm.knowledge_id, migrateForm.document_id, [...targetParagraphIds.value])
    .then(() => {
      MsgSuccess('迁移成功')
      migrationSucceeded.value = true
      visible.value = false
    })
    .catch(() => {
      // 请求层统一提示错误，保留表单。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBeforeClose(done: () => void) {
  if (!loading.value && !optionLoading.value) done()
}

function handleClosed() {
  const migratedParagraphIds = migrationSucceeded.value ? [...targetParagraphIds.value] : []
  // 关闭动画结束后通知页面，使用打开时固定的 ID，不读取当前勾选。
  if (migratedParagraphIds.length) emit('success', migratedParagraphIds)
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="迁移至" :before-close="handleBeforeClose" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="loading || optionLoading"
      :model="migrateForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="选择知识库" prop="knowledge_id">
        <el-select
          v-model="migrateForm.knowledge_id"
          fit-input-width
          filterable
          placeholder="请选择知识库"
          :loading="knowledgeLoading"
          @change="handleKnowledgeChange"
        >
          <template v-for="knowledge in knowledgeOptions" :key="knowledge.id">
            <el-option :label="knowledge.name" :value="knowledge.id">
              <div class="flex-align-center min-w-0 gap-2">
                <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0" />
                <span class="truncate" :title="knowledge.name">{{ knowledge.name }}</span>
              </div>
            </el-option>
          </template>
          <template #label="{ label, value }">
            <span class="flex-align-center gap-2">
              <KnowledgeIcon :type="knowledgeById.get(value)?.type" :size="20" class="shrink-0" />
              <span class="truncate" :title="label">{{ label }}</span>
            </span>
          </template>
        </el-select>
      </el-form-item>
      <el-form-item label="保存到文档" prop="document_id">
        <el-select
          v-model="migrateForm.document_id"
          fit-input-width
          filterable
          placeholder="请选择文档"
          :loading="documentLoading"
          :disabled="!migrateForm.knowledge_id"
        >
          <template v-for="document in documentOptions" :key="document.id">
            <el-option :label="document.name" :value="document.id">
              <div class="flex-align-center min-w-0 gap-2">
                <img :src="getFileIconUrl(document.name)" alt="" class="size-5 shrink-0" />
                <span class="truncate" :title="document.name">{{ document.name }}</span>
              </div>
            </el-option>
          </template>
          <template #label="{ label }">
            <span class="flex-align-center gap-2">
              <img :src="getFileIconUrl(label)" alt="" class="size-5 shrink-0" />
              <span class="truncate" :title="label">{{ label }}</span>
            </span>
          </template>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消迁移分段 -->
      <el-button plain :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 确认迁移分段 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
