<script setup lang="ts">
import { ref } from 'vue'
import type { KnowledgeItem } from '@/api/types'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ButtonMigrateDocument' })
const props = defineProps<{ knowledgeId: string; documentIds: string[]; disabled?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const optionLoading = ref(false)
const knowledgeOptions = ref<KnowledgeItem[]>([])
const targetKnowledgeId = ref('')
const targetDocumentIds = ref<string[]>([])

function handleOpenDialog() {
  if (props.disabled || loading.value || optionLoading.value || !props.documentIds.length) return
  const ids = props.documentIds
  targetDocumentIds.value = [...ids]
  targetKnowledgeId.value = ''
  visible.value = true
  optionLoading.value = true
  KnowledgeApi.getAllKnowledge()
    .then((knowledge) => {
      knowledgeOptions.value = knowledge.filter(({ id }) => id !== props.knowledgeId)
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      optionLoading.value = false
    })
}

function handleSubmit() {
  if (!targetKnowledgeId.value || loading.value) return
  loading.value = true
  return DocumentApi.putMigrateDocuments(props.knowledgeId, targetKnowledgeId.value, targetDocumentIds.value)
    .then(() => {
      MsgSuccess('迁移成功')
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
  targetKnowledgeId.value = ''
  targetDocumentIds.value = []
  knowledgeOptions.value = []
}
</script>

<template>
  <!-- 文档迁移入口 -->
  <MkAction label="迁移" icon="icon_move2_outlined" :disabled="disabled || loading || !documentIds.length" @click="handleOpenDialog" />
  <MkDialog v-model="visible" title="迁移文档" :show-close="!loading && !optionLoading" @closed="handleClosed">
    <el-form label-position="top" @submit.prevent>
      <el-form-item label="目标知识库" required>
        <el-select v-model="targetKnowledgeId" filterable placeholder="请选择知识库" :loading="optionLoading" :disabled="loading">
          <template v-for="target in knowledgeOptions" :key="target.id">
            <el-option :label="target.name" :value="target.id" />
          </template>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消文档迁移 -->
      <el-button :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 确认迁移文档 -->
      <el-button type="primary" :loading="loading" :disabled="!targetKnowledgeId || optionLoading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
