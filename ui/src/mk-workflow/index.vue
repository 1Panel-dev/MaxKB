<script setup lang="ts">
import LogicFlow, { type BaseNodeModel, type GraphModel } from '@logicflow/core'
import '@logicflow/core/dist/index.css'
import { SelectionSelect } from '@logicflow/extension'
import '@logicflow/extension/lib/index.css'
import { BasicComponentsNode } from '@/mk-workflow/core/data'
import AppEdge from '@/mk-workflow/core/edge'
import { initDefaultShortcut } from '@/mk-workflow/core/shortcut'
import { applicationTemplate } from '@/mk-workflow/core/template'
import { disconnectAll, getTeleport } from '@/mk-workflow/core/teleport'
import Dagre from '@/mk-workflow/plugins/dagre'
import { WorkflowMode, WorkflowNodeType } from '@/mk-workflow/types'

defineOptions({ name: 'MkWorkflow' })

type WorkflowNodeModel = BaseNodeModel & {
  clear_next_node_field?: (containSelf: boolean) => void
  set_loop_body?: () => void
  validate?: () => Promise<unknown> | unknown
}

type WorkflowGraphModel = GraphModel & {
  get_provide: (
    node: LogicFlow.NodeData | null,
    graph: GraphModel | null,
  ) => {
    getGraph: () => GraphModel | null
    getNode: () => LogicFlow.NodeData | null
    workflowMode: WorkflowMode
  }
}

type ShapeItem = {
  callback?: (logicFlow: LogicFlow, container?: HTMLElement) => void
  className?: string
  disabled?: boolean
  icon?: string
  label?: string
  properties?: LogicFlow.PropertiesType
  text?: string
  type?: string
}

type AnchorDropEvent = {
  nodeModel?: WorkflowNodeModel
}

const props = withDefaults(
  defineProps<{
    data?: LogicFlow.GraphConfigData | null
  }>(),
  { data: null },
)

const nodeModules = import.meta.glob<{ default: LogicFlow.RegisterConfig }>('./nodes/**/index.ts', {
  eager: true,
})
const TeleportContainer = getTeleport()
const logicFlowRef = shallowRef<LogicFlow>()
const containerRef = useTemplateRef<HTMLDivElement>('containerRef')
const flowId = ref('')

let shortcutCleanup: (() => void) | undefined
let fitViewTimer: ReturnType<typeof setTimeout> | undefined

function resolveShapeItem(shapeItem: ShapeItem | WorkflowNodeType): ShapeItem | undefined {
  if (typeof shapeItem !== 'string') return shapeItem
  return BasicComponentsNode[shapeItem]
}

function renderGraphData(
  data: LogicFlow.GraphConfigData = props.data ?? applicationTemplate.blank,
) {
  const container = containerRef.value
  if (!container) return

  shortcutCleanup?.()
  logicFlowRef.value?.destroy()

  logicFlowRef.value = new LogicFlow({
    plugins: [Dagre, SelectionSelect],
    textEdit: false,
    adjustEdge: false,
    adjustEdgeStartAndEnd: false,
    background: { backgroundColor: '#f5f6f7' },
    grid: {
      size: 10,
      type: 'dot',
      config: { color: '#DEE0E3', thickness: 1 },
    },
    keyboard: { enabled: true },
    isSilentMode: false,
    container,
  })

  logicFlowRef.value.setTheme({
    bezier: { stroke: '#afafaf', strokeWidth: 1 },
  })
  logicFlowRef.value.on('graph:rendered', () => {
    flowId.value = logicFlowRef.value.graphModel.flowId ?? ''
  })
  logicFlowRef.value.on('node:delete', () => {
    // 节点搜索组件迁入后在这里触发重新搜索。
  })

  shortcutCleanup = initDefaultShortcut(logicFlowRef.value, logicFlowRef.value.graphModel)
  logicFlowRef.value.batchRegister([...Object.values(nodeModules).map(({ default: node }) => node), AppEdge])
  logicFlowRef.value.setDefaultEdgeType('app-edge')
  logicFlowRef.value.render(structuredClone(data))

  const workflowGraphModel = logicFlowRef.value.graphModel as WorkflowGraphModel
  workflowGraphModel.get_provide = (node, graph) => ({
    getNode: () => node,
    getGraph: () => graph,
    workflowMode: WorkflowMode.Application,
  })
  workflowGraphModel.eventCenter.on('delete_edge', (edgeIds: string[]) => {
    edgeIds.forEach((edgeId) => logicFlowRef.value?.deleteEdge(edgeId))
  })
  workflowGraphModel.eventCenter.on('anchor:drop', (event: AnchorDropEvent) => {
    event.nodeModel?.clear_next_node_field?.(false)
  })

  // fitViewTimer = setTimeout(() => {
  //   if (logicFlowRef.value.graphModel.nodes.length > 1) logicFlowRef.value.fitView()
  //   else logicFlowRef.value.translateCenter()
  // }, 500)
}

function render(data: LogicFlow.GraphConfigData) {
  logicFlowRef.value?.render(data)
}

function validate() {
  if (!logicFlowRef.value) return Promise.resolve([])
  return Promise.all(
    logicFlowRef.value.graphModel.nodes.map((node) => (node as WorkflowNodeModel).validate?.()),
  )
}

function getGraphData(): LogicFlow.GraphData | undefined {
  if (!logicFlowRef.value) return

  const graphData = logicFlowRef.value.getGraphData() as LogicFlow.GraphData
  graphData.nodes.forEach((node) => {
    if (node.type === WorkflowNodeType.LoopBodyNode) {
      const node_model = logicFlowRef.value?.getNodeModelById(node.id)
      node_model?.set_loop_body()
    }
  })

  const normalizedGraphData = logicFlowRef.value.getGraphData() as LogicFlow.GraphData
  return {
    nodes: normalizedGraphData.nodes.filter((node) => node.type !== WorkflowNodeType.LoopBodyNode),
    edges: graphData.edges.filter((edge) => edge.type !== 'loop-edge'),
  }
}

function onmousedown(input: ShapeItem) {
  if (!logicFlowRef.value) return

  if (input.type) {
    logicFlowRef.value.dnd.startDrag({
      type: input.type,
      properties: structuredClone(input.properties ?? {}),
    })
  }
  input.callback?.(logicFlowRef.value)
}

function addNode(input: ShapeItem | WorkflowNodeType) {
  const shapeItem = resolveShapeItem(input)
  if (!logicFlowRef.value || !shapeItem?.type) return

  logicFlowRef.value.clearSelectElements()
  const containerRect = logicFlowRef.value.container.getBoundingClientRect()
  const { canvasOverlayPosition } = logicFlowRef.value.getPointByClient(
    containerRect.left + containerRect.width / 2,
    containerRect.top + containerRect.height / 2,
  )
  const newNode = logicFlowRef.value.graphModel.addNode({
    type: shapeItem.type,
    properties: structuredClone(shapeItem.properties ?? {}),
    x: canvasOverlayPosition.x,
    y: canvasOverlayPosition.y,
  })
  newNode.isSelected = true
  newNode.isHovered = true
  logicFlowRef.value.toFront(newNode.id)
}

function clearGraphData() {
  logicFlowRef.value?.clearData()
}

function fitView() {
  nextTick(() => logicFlowRef.value?.fitView())
}

onMounted(() => renderGraphData())
onBeforeUnmount(() => {
  if (fitViewTimer) clearTimeout(fitViewTimer)
  shortcutCleanup?.()
  logicFlowRef.value?.destroy()
  disconnectAll()
})

defineExpose({
  onmousedown,
  validate,
  getGraphData,
  addNode,
  clearGraphData,
  renderGraphData,
  render,
  fitView,
})
</script>

<template>
  <div class="relative h-full w-full overflow-hidden">
    <div id="graph" ref="containerRef" class="h-full w-full" />
    <TeleportContainer :flow-id="flowId" />
  </div>
</template>
