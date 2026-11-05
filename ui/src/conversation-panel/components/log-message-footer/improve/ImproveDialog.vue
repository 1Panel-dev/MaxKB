<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import WorkspaceKnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import WorkspaceDocumentApi from '@/api/admin/workspace/knowledge/document'
import SystemResourceDocumentApi from '@/api/admin/system/resource-management/knowledge/document'
import { isSystemResource } from '@/utils/resource-context'
import type { DocumentItem, KnowledgeItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'ImproveDialog' })
const props = defineProps<{
  api: Pick<typeof ChatLogApi, 'putChatRecordLog'>
  applicationId: string
  chatId: string
  recordId: string
  question: string
  answer: string
}>()

const emit = defineEmits<{ closed: []; saved: [] }>()

// 查询当前资源范围的知识库与联动文档选项。
const visible = ref(false)
const loading = ref(false)
const knowledgeLoading = ref(false)
const documentLoading = ref(false)
const optionLoading = computed(() => knowledgeLoading.value || documentLoading.value)
const knowledgeOptions = ref<KnowledgeItem[]>([])
const documentOptions = ref<DocumentItem[]>([])
const knowledgeById = computed(() => new Map(knowledgeOptions.value.map((knowledge) => [knowledge.id, knowledge])))
const formRef = useTemplateRef<FormInstance>('formRef')
const improveForm = reactive({
  knowledge_id: '',
  document_id: '',
  problem_text: props.question,
  content: props.answer,
  title: '',
})
const rules: FormRules<typeof improveForm> = {
  problem_text: [
    { required: true, whitespace: true, message: '请输入关联问题', trigger: 'blur' },
    { max: 64, message: '关联问题不能超过64个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, whitespace: true, message: '请输入内容', trigger: 'blur' },
    { max: 100000, message: '内容不能超过100000个字符', trigger: 'blur' },
  ],
  knowledge_id: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  document_id: [{ required: true, message: '请选择文档', trigger: 'change' }],
}

function open() {
  if (visible.value || loading.value || optionLoading.value) return
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
  improveForm.document_id = ''
  documentOptions.value = []
  formRef.value?.clearValidate('document_id')
  if (!knowledgeId) return
  documentLoading.value = true
  const requestDocumentApi = isSystemResource() ? SystemResourceDocumentApi : WorkspaceDocumentApi
  return requestDocumentApi
    .getAllDocuments(knowledgeId)
    .then((documents) => {
      if (improveForm.knowledge_id === knowledgeId) documentOptions.value = documents
    })
    .catch(() => {
      // 请求层统一提示错误，文档保持空选。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

// 保存修正内容，失败保留草稿。
async function handleSubmit() {
  if (loading.value || optionLoading.value) return
  if (!(await formRef.value?.validate().catch(() => false)) || loading.value) return
  loading.value = true
  return props.api
    .putChatRecordLog(props.applicationId, props.chatId, props.recordId, improveForm.knowledge_id, improveForm.document_id, {
      title: improveForm.title.trim(),
      content: improveForm.content.trim(),
      problem_text: improveForm.problem_text.trim(),
    })
    .then(() => {
      emit('saved')
      MsgSuccess('保存成功')
      visible.value = false
    })
    .catch(() => {
      // 请求层统一提示错误，保留表单。
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(open)
</script>

<template>
  <MkDialog v-model="visible" title="修正内容" @closed="emit('closed')">
    <el-form
      ref="formRef"
      v-loading="loading || optionLoading"
      :model="improveForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="关联问题" prop="problem_text">
        <el-input v-model="improveForm.problem_text" maxlength="64" show-word-limit placeholder="请输入关联问题" />
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input v-model="improveForm.content" type="textarea" :rows="10" maxlength="100000" show-word-limit placeholder="请输入内容" />
      </el-form-item>
      <el-form-item label="标题" prop="title">
        <el-input v-model="improveForm.title" maxlength="256" placeholder="请给当前内容设置一个标题，以便管理查看" />
      </el-form-item>
      <el-form-item label="选择知识库" prop="knowledge_id">
        <el-select
          v-model="improveForm.knowledge_id"
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
          v-model="improveForm.document_id"
          fit-input-width
          filterable
          placeholder="请选择文档"
          :loading="documentLoading"
          :disabled="!improveForm.knowledge_id"
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
      <!-- 取消修正内容 -->
      <el-button plain :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 保存修正内容 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
