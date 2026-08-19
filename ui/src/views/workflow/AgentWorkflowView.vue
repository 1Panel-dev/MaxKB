<script setup lang="ts">
import type LogicFlow from '@logicflow/core'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import {nodeDict} from "@/workflow-canvas/config/node-mapping.ts"
import WorkflowComponentMenu from './components/WorkflowComponentMenu.vue'
import {type ShapeItem} from "@/workflow-canvas/types"
defineOptions({ name: 'AgentWorkflowView' })

defineProps<{
  agentId: string
}>()

const emit = defineEmits<{
  save: [data: LogicFlow.GraphData]
}>()

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

const handleAddNode = (nodeType: WorkflowNodeType) => {
  const shapeItem=toShapeItem(nodeType)
  if(!shapeItem){
     return
  }
  workflowRef.value?.addNode(shapeItem)
  }

const toShapeItem=(nodeType: WorkflowNodeType)=>{
 const node=nodeDict[nodeType]
  if(node){
  const shapeItem:ShapeItem={
   type: node.type,
   properties:node.properties,
   text:node.text
  }
  return shapeItem;
}
}
const handleSave = () => {
  const graphData = workflowRef.value?.getGraphData()
  if (graphData) emit('save', graphData)
}
</script>

<template>
  <main class="flex h-screen w-screen flex-col overflow-hidden">
    <header
      class="h-header flex shrink-0 items-center justify-end gap-3 border-b border-N300 bg-white px-6"
    >
      <WorkflowComponentMenu @select="handleAddNode" />
      <el-button @click="handleSave"> 保存 </el-button>
    </header>
    <!-- 主画布 -->
    <WorkflowCanvas ref="workflowRef" class="min-h-0 flex-1" />
  </main>
</template>
