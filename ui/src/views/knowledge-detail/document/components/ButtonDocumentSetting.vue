<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { DOCUMENT_HIT_HANDLING, KNOWLEDGE_TYPE } from '@/api/enums'
import type { DocumentItem, DocumentSettingPayload } from '@/api/types'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import { DOCUMENT_HIT_HANDLING_LABELS } from '@/constants/document'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ButtonDocumentSetting' })
const props = defineProps<{ knowledgeId: string; documents: DocumentItem[]; batch?: boolean; disabled?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const document = ref<DocumentItem>()
const targetDocumentIds = ref<string[]>([])
const form = ref({
  hit_handling_method: DOCUMENT_HIT_HANDLING.OPTIMIZATION as DocumentSettingPayload['hit_handling_method'],
  directly_return_similarity: 0.9,
  source_url: '',
  selector: '',
  allow_download: true,
})

function handleOpenDialog() {
  if (props.disabled || loading.value || !props.documents.length) return
  const documents = props.documents
  const batch = props.batch
  document.value = batch ? undefined : documents[0]
  targetDocumentIds.value = documents.map(({ id }) => id)
  const current = document.value
  form.value = {
    hit_handling_method: current?.hit_handling_method ?? DOCUMENT_HIT_HANDLING.OPTIMIZATION,
    directly_return_similarity: current?.directly_return_similarity ?? 0.9,
    source_url: String(current?.meta?.source_url ?? ''),
    selector: String(current?.meta?.selector ?? ''),
    allow_download: current?.meta?.allow_download !== false,
  }
  visible.value = true
}

async function handleSubmit() {
  if (loading.value || !(await formRef.value?.validate().catch(() => false))) return
  loading.value = true
  const data: DocumentSettingPayload = {
    hit_handling_method: form.value.hit_handling_method,
    directly_return_similarity: form.value.directly_return_similarity,
  }
  let request: Promise<unknown>
  if (document.value) {
    data.meta = { ...document.value.meta, allow_download: form.value.allow_download }
    if (document.value.type === KNOWLEDGE_TYPE.WEB) {
      data.meta.source_url = form.value.source_url.trim()
      data.meta.selector = form.value.selector
    }
    request = DocumentApi.putDocumentSetting(props.knowledgeId, document.value.id, data)
  } else {
    request = DocumentApi.putBatchDocumentSetting(props.knowledgeId, targetDocumentIds.value, { ...data, allow_download: form.value.allow_download })
  }
  return request
    .then(() => {
      MsgSuccess('设置成功')
      visible.value = false
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  document.value = undefined
  targetDocumentIds.value = []
  formRef.value?.clearValidate()
}
</script>

<template>
  <!-- 文档设置入口 -->
  <MkAction label="设置" icon="icon_setting" :disabled="disabled || loading || !documents.length" @click="handleOpenDialog" />
  <MkDialog v-model="visible" title="文档设置" :show-close="!loading" @closed="handleClosed">
    <el-form ref="formRef" :model="form" label-position="top" :disabled="loading" @submit.prevent>
      <template v-if="document?.type === KNOWLEDGE_TYPE.WEB">
        <el-form-item
          label="文档地址"
          prop="source_url"
          :rules="[
            { required: true, message: '请输入文档地址', trigger: 'blur' },
            { whitespace: true, message: '文档地址不能为空白', trigger: 'blur' },
          ]"
        >
          <el-input v-model="form.source_url" />
        </el-form-item>
        <el-form-item label="选择器"><el-input v-model="form.selector" /></el-form-item>
      </template>
      <el-form-item label="召回处理">
        <el-radio-group v-model="form.hit_handling_method">
          <template v-for="(label, value) in DOCUMENT_HIT_HANDLING_LABELS" :key="value">
            <el-radio :value="value">{{ label }}</el-radio>
          </template>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="form.hit_handling_method === DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN" label="相似度阈值">
        <el-input-number
          v-model="form.directly_return_similarity"
          :min="0"
          :max="1"
          :precision="3"
          :step="0.1"
          :value-on-clear="0"
          controls-position="right"
          align="left"
        />
      </el-form-item>
      <el-checkbox v-model="form.allow_download">{{ document?.type === KNOWLEDGE_TYPE.WEB ? '允许预览' : '允许下载' }}</el-checkbox>
    </el-form>
    <template #footer>
      <!-- 取消文档设置 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存文档设置 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
