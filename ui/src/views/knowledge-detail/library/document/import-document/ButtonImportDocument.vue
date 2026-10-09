<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef, type Component } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type LogicFlow from '@logicflow/core'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import WebImportDocumentDrawer from './WebImportDocumentDrawer.vue'
import LarkImportDocumentDrawer from './LarkImportDocumentDrawer.vue'
import WorkflowImportDocumentDrawer from './WorkflowImportDocumentDrawer.vue'

defineOptions({ name: 'ButtonImportDocument' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  knowledgeType: string
  folderToken?: string
  workflow?: LogicFlow.GraphConfigData
}>()
const emit = defineEmits<{ refresh: [] }>()

/* 导入入口：按知识库类型挂载独立抽屉，关闭动画后卸载。 */
const drawerMounted = ref(false)
const drawerComponent = computed<Component | undefined>(() => {
  switch (props.knowledgeType) {
    case KNOWLEDGE_TYPE_KEY.WEB:
      return WebImportDocumentDrawer
    case KNOWLEDGE_TYPE_KEY.LARK:
      return LarkImportDocumentDrawer
    case KNOWLEDGE_TYPE_KEY.WORKFLOW:
      return WorkflowImportDocumentDrawer
    default:
      return undefined
  }
})
const drawerProps = computed(() => {
  if (props.knowledgeType === KNOWLEDGE_TYPE_KEY.WORKFLOW) return { knowledgeId: props.knowledgeId, workflow: props.workflow }
  if (props.knowledgeType === KNOWLEDGE_TYPE_KEY.LARK) {
    return { api: props.api, knowledgeId: props.knowledgeId, folderToken: props.folderToken ?? '' }
  }
  return { api: props.api, knowledgeId: props.knowledgeId }
})
const drawerRef = useTemplateRef<{ open: () => void }>('drawerRef')
function handleOpenImport() {
  if (!drawerComponent.value || drawerMounted.value) return
  drawerMounted.value = true
  nextTick(() => drawerRef.value?.open())
}
</script>

<template>
  <!-- 导入文档 -->
  <el-button type="primary" @click="handleOpenImport">
    <MkIcon name="icon_import_outlined" />
    <span>导入文档</span>
  </el-button>
  <component
    :is="drawerComponent"
    v-if="drawerMounted"
    ref="drawerRef"
    v-bind="drawerProps"
    @refresh="emit('refresh')"
    @closed="drawerMounted = false"
  />
</template>
