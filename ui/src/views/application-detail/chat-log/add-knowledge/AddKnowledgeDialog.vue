<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationChatLogApi } from '../../context'
import WorkspaceKnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import WorkspaceDocumentApi from '@/api/admin/workspace/knowledge/document'
import SystemResourceDocumentApi from '@/api/admin/system/resource-management/knowledge/document'
import { isSystemResource } from '@/utils/resource-context'
import type { DocumentItem, KnowledgeItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'AddKnowledgeDialog' })
const props = defineProps<{
  api: ApplicationChatLogApi
  applicationId: string
}>()

const emit = defineEmits<{ refresh: [] }>()

// 固定本次勾选的对话，查询知识库与联动文档选项。
const visible = ref(false)
const refreshOnClosed = ref(false)
const loading = ref(false)
const knowledgeLoading = ref(false)
const documentLoading = ref(false)
const optionLoading = computed(() => knowledgeLoading.value || documentLoading.value)
const targetChatIds = ref<string[]>([])
const knowledgeOptions = ref<KnowledgeItem[]>([])
const documentOptions = ref<DocumentItem[]>([])
const knowledgeById = computed(() => new Map(knowledgeOptions.value.map((knowledge) => [knowledge.id, knowledge])))
const formRef = useTemplateRef<FormInstance>('formRef')
const knowledgeForm = reactive({ knowledge_id: '', document_id: '' })
const rules: FormRules<typeof knowledgeForm> = {
  knowledge_id: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  document_id: [{ required: true, message: '请选择文档', trigger: 'change' }],
}

function open(chatIds: string[]) {
  if (visible.value || loading.value || optionLoading.value || !chatIds.length) return
  targetChatIds.value = [...chatIds]
  visible.value = true
  knowledgeLoading.value = true
  const requestKnowledgeApi = isSystemResource() ? SystemResourceKnowledgeApi : WorkspaceKnowledgeApi
  return requestKnowledgeApi
    .getAllKnowledge()
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
  knowledgeForm.document_id = ''
  documentOptions.value = []
  formRef.value?.clearValidate('document_id')
  if (!knowledgeId) return
  documentLoading.value = true
  const requestDocumentApi = isSystemResource() ? SystemResourceDocumentApi : WorkspaceDocumentApi
  return requestDocumentApi
    .getAllDocuments(knowledgeId)
    .then((documents) => {
      documentOptions.value = documents
    })
    .catch(() => {
      // 请求层统一提示错误，文档保持空选。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

// 添加成功后关闭并刷新日志，失败保留当前选择以便重试。
async function handleSubmit() {
  if (loading.value || optionLoading.value || !targetChatIds.value.length) return
  if (!(await formRef.value?.validate().catch(() => false)) || loading.value) return
  loading.value = true
  return props.api
    .postChatLogAddKnowledge(props.applicationId, { ...knowledgeForm, chat_ids: [...targetChatIds.value] })
    .then(() => {
      MsgSuccess('添加成功')
      refreshOnClosed.value = true
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
  knowledgeForm.knowledge_id = ''
  knowledgeForm.document_id = ''
  targetChatIds.value = []
  knowledgeOptions.value = []
  documentOptions.value = []
  formRef.value?.clearValidate()
  // 批量底栏会随勾选清空而卸载，关闭动画结束后再通知页面刷新。
  if (refreshOnClosed.value) {
    refreshOnClosed.value = false
    emit('refresh')
  }
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加到知识库" :before-close="handleBeforeClose" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="loading || optionLoading"
      :model="knowledgeForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="选择知识库" prop="knowledge_id">
        <el-select
          v-model="knowledgeForm.knowledge_id"
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
          v-model="knowledgeForm.document_id"
          fit-input-width
          filterable
          placeholder="请选择文档"
          :loading="documentLoading"
          :disabled="!knowledgeForm.knowledge_id"
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
      <!-- 取消添加到知识库 -->
      <el-button plain :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 确认添加到知识库 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
