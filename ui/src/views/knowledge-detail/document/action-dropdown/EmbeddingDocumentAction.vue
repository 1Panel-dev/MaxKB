<script setup lang="ts">
import { computed, ref } from 'vue'
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentItem } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EmbeddingDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  documentIds: string[]
  document?: DocumentItem
  batch?: boolean
  display?: 'menu' | 'button'
}>()
const operationLoading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const targetDocumentIds = ref<string[]>([])
const scope = ref<'error' | 'all'>('error')

// 单项向量化根据任务状态切换为取消入口，批量入口始终打开向量化配置。
const running = computed(() => {
  if (props.batch) return false
  const state = props.document?.status?.at(-DOCUMENT_TASK_TYPE.EMBEDDING)
  return state === DOCUMENT_TASK_STATE.PENDING || state === DOCUMENT_TASK_STATE.STARTED
})

function handleEmbedding() {
  if (!running.value) {
    targetDocumentIds.value = [...props.documentIds]
    scope.value = 'error'
    visible.value = true
    return
  }
  // 正在排队或执行时，直接提交取消向量化请求。
  operationLoading.value = true
  return props.api
    .putBatchCancelDocumentTask(props.knowledgeId, [...props.documentIds], DOCUMENT_TASK_TYPE.EMBEDDING)
    .then(() => {
      MsgSuccess('操作成功')
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      operationLoading.value = false
    })
}

// 根据选定的分段范围提交向量化，失败时保留配置。
function handleSubmit() {
  if (loading.value) return
  loading.value = true
  const stateList = Object.values(DOCUMENT_TASK_STATE).filter((state) => scope.value === 'all' || state !== DOCUMENT_TASK_STATE.SUCCESS)
  return props.api
    .putBatchRefreshDocuments(props.knowledgeId, targetDocumentIds.value, stateList)
    .then(() => {
      MsgSuccess('任务已提交')
      visible.value = false
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  targetDocumentIds.value = []
  scope.value = 'error'
}
</script>

<template>
  <!-- 批量向量化 -->
  <el-button v-if="batch" :disabled="operationLoading || loading || !documentIds.length" @click="handleEmbedding">向量化</el-button>
  <!-- 向量化或取消向量化 -->
  <MkAction
    v-else
    :display="display ?? 'menu'"
    :label="running ? '取消向量化' : '向量化'"
    :icon="running ? 'icon_close_outlined' : 'icon_refresh_outlined'"
    :disabled="operationLoading || loading || !documentIds.length"
    @click="handleEmbedding"
  />
  <MkDialog v-model="visible" title="向量化" @closed="handleClosed">
    <el-form label-position="top" @submit.prevent>
      <el-form-item label="选择分段">
        <el-radio-group v-model="scope">
          <el-radio value="error">未成功的分段</el-radio>
          <el-radio value="all">全部分段</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消向量化配置 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 提交向量化 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
