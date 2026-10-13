<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentItem } from '@/api/types'
import DocumentTagsDrawer from './DocumentTagsDrawer.vue'

defineOptions({ name: 'DocumentTagsAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  document: DocumentItem
  label: string
  icon?: string
  disabled?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

const drawerMounted = ref(false)
const documentTagsRef = useTemplateRef<InstanceType<typeof DocumentTagsDrawer>>('documentTagsRef')
const targetKnowledgeId = ref('')
let tagsChanged = false

function handleOpenDrawer() {
  if (props.disabled || loading.value || drawerMounted.value) return
  targetKnowledgeId.value = props.knowledgeId
  const documentId = props.document.id
  drawerMounted.value = true
  return nextTick(() => documentTagsRef.value?.open(documentId))
}

function handleTagsChanged() {
  // 抽屉内立即刷新，关闭后再统一刷新文档列表。
  tagsChanged = true
}

function handleDrawerClosed() {
  drawerMounted.value = false
  if (tagsChanged) {
    tagsChanged = false
    emit('refresh')
  }
}
</script>

<template>
  <!-- 文档标签设置入口 -->
  <MkAction :label="label" :icon="icon" :disabled="disabled || loading" @click="handleOpenDrawer" />
  <DocumentTagsDrawer
    v-if="drawerMounted"
    ref="documentTagsRef"
    v-model:loading="loading"
    :api="api"
    :knowledge-id="targetKnowledgeId"
    @refresh="handleTagsChanged"
    @closed="handleDrawerClosed"
  />
</template>
