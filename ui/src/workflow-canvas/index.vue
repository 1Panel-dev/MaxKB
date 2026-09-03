<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, shallowRef, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import LogicFlow, { type GraphModel } from '@logicflow/core'
import '@logicflow/core/dist/index.css'
import { SelectionSelect } from '@logicflow/extension'
import '@logicflow/extension/lib/index.css'
import AppEdge from '@/workflow-canvas/core/edge/index'
import { initDefaultShortcut } from '@/workflow-canvas/core/shortcut'
import { disconnectAll, getTeleport } from '@/workflow-canvas/core/teleport'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import Dagre from '@/workflow-canvas/plugins/dagre'
import modelAPI from '@/api/admin/workspace/model/model'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import { type ShapeItem } from '@/workflow-canvas/types'
import type { NodeMenuCurrentResource } from '@/workflow-canvas/node-menu/types'
defineOptions({ name: 'MkWorkflow' })

type CanvasWorkflowNodeModel = WorkflowNodeModel & { set_loop_body?: () => void }

const props = withDefaults(
  defineProps<{
    currentResource?: NodeMenuCurrentResource
    data?: LogicFlow.GraphConfigData | null
    loopWorkflowMode?: WorkflowMode
    workflowMode?: WorkflowMode
  }>(),
  {
    data: null,
    loopWorkflowMode: WorkflowMode.ApplicationLoop,
    workflowMode: WorkflowMode.Application,
  },
)

const nodeModules = import.meta.glob<{ default: LogicFlow.RegisterConfig }>('./nodes/**/index.ts', { eager: true })

const TeleportContainer = getTeleport()
const lf = shallowRef<LogicFlow>()
const containerRef = useTemplateRef<HTMLDivElement>('containerRef')
const flowId = ref('')

let fitViewTimer: ReturnType<typeof setTimeout> | undefined

function renderGraphData(data: LogicFlow.GraphConfigData = props.data ?? {}) {
  const container = containerRef.value
  if (!container) return

  lf.value = new LogicFlow({
    plugins: [Dagre, SelectionSelect],
    textEdit: false,
    adjustEdge: false,
    adjustEdgeStartAndEnd: false,
    background: { backgroundColor: '#f5f6f7' },
    grid: { size: 20, type: 'dot', config: { color: '#DEE0E3', thickness: 1 } },
    keyboard: { enabled: true },
    isSilentMode: false,
    container,
  })

  lf.value.setTheme({ bezier: { stroke: '#afafaf', strokeWidth: 1 } })
  lf.value.on('graph:rendered', () => {
    flowId.value = lf.value?.graphModel.flowId ?? ''
  })
  lf.value.on('node:delete', () => {
    // 节点搜索组件迁入后在这里触发重新搜索。
  })

  initDefaultShortcut(lf.value, lf.value.graphModel)
  lf.value.batchRegister([...Object.values(nodeModules).map(({ default: node }) => node), AppEdge])
  lf.value.setDefaultEdgeType('app-edge')
  lf.value.render(data ? data : {})

  lf.value.graphModel.get_provide = (model: LogicFlow.NodeData | null, graph: GraphModel | null) => ({
    getModel: () => model,
    getGraph: () => graph,
    workflowMode: props.workflowMode,
    loopWorkflowMode: props.loopWorkflowMode,
    currentResource: props.currentResource,
    apiType: 'workspace',
    getSelectModelList: (params: { model_type: string }) => modelAPI.getModelList(params),
    getModelParamsForm: (modelId: string) => modelAPI.getModelParamsForm(modelId),
    startDragNode: onmousedown,
  })
  lf.value.graphModel.eventCenter.on('delete_edge', (edgeIds: string[]) => {
    edgeIds.forEach((edgeId) => lf.value?.deleteEdge(edgeId))
  })
  lf.value.graphModel.eventCenter.on('anchor:drop', (event) => {
    const nodeModel = event.nodeModel as unknown as WorkflowNodeModel
    nodeModel.clearNextNodeField(false)
  })

  fitViewTimer = setTimeout(() => {
    if (lf.value && lf.value.graphModel?.nodes.length > 1) lf.value?.fitView()
    else lf.value?.translateCenter()
  }, 500)
}

function getGraphData(): LogicFlow.GraphData | undefined {
  if (!lf.value) return

  const graphData = lf.value.getGraphData() as LogicFlow.GraphData
  graphData.nodes.forEach((node) => {
    if (node.type === WorkflowNodeType.LoopBodyNode) {
      const node_model = lf.value?.getNodeModelById(node.id)
      const workflowNodeModel = node_model as CanvasWorkflowNodeModel | undefined
      workflowNodeModel?.setLoopBody?.()
    }
  })

  const normalizedGraphData = lf.value.getGraphData() as LogicFlow.GraphData
  return {
    nodes: normalizedGraphData.nodes.filter((node) => node.type !== WorkflowNodeType.LoopBodyNode),
    edges: graphData.edges.filter((edge) => edge.type !== 'loop-edge'),
  }
}

function render(data: LogicFlow.GraphConfigData) {
  lf.value?.render(data)
}

function validate() {
  if (!lf.value) return Promise.resolve([])
  return Promise.all(lf.value.graphModel.nodes.map((node) => (node as unknown as WorkflowNodeModel).validate?.()))
}

function onmousedown(shapeItem: ShapeItem, event?: PointerEvent) {
  if (!lf.value) return

  if (shapeItem.type) {
    lf.value.dnd.startDrag({ type: shapeItem.type, properties: cloneDeep(shapeItem.properties ?? {}) })

    if (event) {
      const containerRect = lf.value.container.getBoundingClientRect()
      const isInsideCanvas =
        event.clientX >= containerRect.left &&
        event.clientX <= containerRect.right &&
        event.clientY >= containerRect.top &&
        event.clientY <= containerRect.bottom

      if (isInsideCanvas) lf.value.dnd.dragEnter(event)
    }
  }
  shapeItem.callback?.(lf.value)
}

function addNode(shapeItem: ShapeItem) {
  if (!lf.value) return
  lf.value.clearSelectElements()
  const containerRect = lf.value.container.getBoundingClientRect()
  const { canvasOverlayPosition } = lf.value.getPointByClient(
    containerRect.left + containerRect.width / 2,
    containerRect.top + containerRect.height / 2,
  )
  const newNode = lf.value.graphModel.addNode({
    type: shapeItem.type as string,
    properties: cloneDeep(shapeItem.properties ?? {}),
    x: canvasOverlayPosition.x,
    y: canvasOverlayPosition.y,
  })
  newNode.isSelected = true
  newNode.isHovered = true
  lf.value.toFront(newNode.id)
}

function clearGraphData() {
  lf.value?.clearData()
}

function fitView() {
  nextTick(() => lf.value?.fitView())
}

onMounted(() => renderGraphData())
onBeforeUnmount(() => {
  if (fitViewTimer) clearTimeout(fitViewTimer)
  lf.value?.destroy()
  disconnectAll()
})

defineExpose({ onmousedown, validate, getGraphData, addNode, clearGraphData, renderGraphData, render, fitView })
</script>

<template>
  <div class="relative h-full w-full">
    <div id="graph" ref="containerRef" class="h-full w-full" />
    <!-- 辅助工具栏 -->
    <TeleportContainer :flow-id="flowId" />
    <!-- // TODO: 临时注释掉，后续加 -->
    <!-- <Control class="workflow-control" v-if="lf" :lf="lf"></Control> -->
    <!-- <NodeSearch :lf="lf" ref="nodeSearchRef"></NodeSearch> -->
  </div>
</template>

<style lang="scss">
@use './style.scss';
</style>
