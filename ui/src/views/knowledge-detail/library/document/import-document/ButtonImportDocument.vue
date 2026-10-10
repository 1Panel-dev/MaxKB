<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
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
const webDrawerMounted = ref(false)
const larkDrawerMounted = ref(false)
const workflowDrawerMounted = ref(false)
const webDrawerRef = useTemplateRef<InstanceType<typeof WebImportDocumentDrawer>>('webDrawerRef')
const larkDrawerRef = useTemplateRef<InstanceType<typeof LarkImportDocumentDrawer>>('larkDrawerRef')
const workflowDrawerRef = useTemplateRef<InstanceType<typeof WorkflowImportDocumentDrawer>>('workflowDrawerRef')

function handleOpenImport() {
  if (webDrawerMounted.value || larkDrawerMounted.value || workflowDrawerMounted.value) return
  switch (props.knowledgeType) {
    case KNOWLEDGE_TYPE_KEY.WEB:
      webDrawerMounted.value = true
      return nextTick(() => webDrawerRef.value?.open())
    case KNOWLEDGE_TYPE_KEY.LARK:
      larkDrawerMounted.value = true
      return nextTick(() => larkDrawerRef.value?.open())
    case KNOWLEDGE_TYPE_KEY.WORKFLOW:
      workflowDrawerMounted.value = true
      return nextTick(() => workflowDrawerRef.value?.open(props.workflow))
  }
}
</script>

<template>
  <!-- 导入文档 -->
  <el-button type="primary" @click="handleOpenImport">
    <MkIcon name="icon_import_outlined" />
    <span>导入文档</span>
  </el-button>
  <WebImportDocumentDrawer
    v-if="webDrawerMounted"
    ref="webDrawerRef"
    :api="api"
    :knowledge-id="knowledgeId"
    @refresh="emit('refresh')"
    @closed="webDrawerMounted = false"
  />
  <LarkImportDocumentDrawer
    v-if="larkDrawerMounted"
    ref="larkDrawerRef"
    :api="api"
    :knowledge-id="knowledgeId"
    :folder-token="folderToken ?? ''"
    @refresh="emit('refresh')"
    @closed="larkDrawerMounted = false"
  />
  <WorkflowImportDocumentDrawer
    v-if="workflowDrawerMounted"
    ref="workflowDrawerRef"
    :knowledge-id="knowledgeId"
    @refresh="emit('refresh')"
    @closed="workflowDrawerMounted = false"
  />
</template>
