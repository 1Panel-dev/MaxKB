<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { KnowledgeDetail } from '@/api/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import WebImportDocumentDrawer from './WebImportDocumentDrawer.vue'
import LarkImportDocumentDrawer from './LarkImportDocumentDrawer.vue'
import WorkflowImportDocumentDrawer from './WorkflowImportDocumentDrawer.vue'

defineOptions({ name: 'ButtonImportDocument' })
const props = defineProps<{ api: typeof DocumentApi; knowledge: KnowledgeDetail }>()
const emit = defineEmits<{ refresh: [] }>()

/* 导入入口：按知识库类型挂载独立抽屉，关闭动画后卸载。 */
const drawerMounted = ref(false)
const drawerComponent = computed(() => {
  switch (props.knowledge.type) {
    case KNOWLEDGE_TYPE.WEB:
      return WebImportDocumentDrawer
    case KNOWLEDGE_TYPE.LARK:
      return LarkImportDocumentDrawer
    case KNOWLEDGE_TYPE.WORKFLOW:
      return WorkflowImportDocumentDrawer
    default:
      return undefined
  }
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
  <el-button v-if="drawerComponent" type="primary" @click="handleOpenImport">
    <MkIcon name="icon_import_outlined" class="mr-1" />
    导入文档
  </el-button>
  <component
    :is="drawerComponent"
    v-if="drawerMounted"
    ref="drawerRef"
    v-bind="knowledge.type === KNOWLEDGE_TYPE.WORKFLOW ? {} : { api }"
    :knowledge="knowledge"
    @refresh="emit('refresh')"
    @closed="drawerMounted = false"
  />
</template>
