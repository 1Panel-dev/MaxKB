<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import ApplicationApi from '@/api/admin/workspace/application'
import { MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { nodeDict } from '@/workflow-canvas/config/node-mapping'
import { WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import WorkflowComponentMenu from './components/WorkflowComponentMenu.vue'

defineOptions({ name: 'ApplicationWorkflowView' })

const route = useRoute()
const applicationId = route.params.applicationId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

function toShapeItem(nodeType: WorkflowNodeType): ShapeItem | undefined {
  const node = nodeDict[nodeType]
  if (!node) return

  return {
    type: node.type,
    properties: node.properties,
    text: node.text,
  }
}

function handleAddNode(nodeType: WorkflowNodeType) {
  const shapeItem = toShapeItem(nodeType)
  if (shapeItem) workflowRef.value?.addNode(shapeItem)
}

// 智能体工作流加载与保存
const loading = ref(false)
function handleSave() {
  const graphData = workflowRef.value?.getGraphData()
  if (!graphData) return

  loading.value = true
  ApplicationApi.putApplication(applicationId, { work_flow: graphData })
    .then(() => {
      MsgSuccess('保存成功')
    })
    .finally(() => {
      loading.value = false
    })
}
const defaultWorkflow = {
  nodes: [],
  deges: [],
}

function loadApplicationDetail() {
  loading.value = true
  ApplicationApi.getApplicationDetail(applicationId)
    .then((application) => {
      //TODO
      workflowRef.value?.render(application.work_flow ?? {})
      workflowRef.value?.fitView()
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(loadApplicationDetail)
</script>

<template>
  <main class="flex h-screen w-screen flex-col overflow-hidden">
    <header
      class="h-header flex shrink-0 items-center justify-end gap-3 border-b border-N300 bg-white px-6"
    >
      <WorkflowComponentMenu @select="handleAddNode" />
      <el-button type="primary" :loading="loading" :disabled="loading" @click="handleSave">
        保存
      </el-button>
    </header>
    <!-- 主画布 -->
    <WorkflowCanvas ref="workflowRef" class="min-h-0 flex-1" />
  </main>
</template>
