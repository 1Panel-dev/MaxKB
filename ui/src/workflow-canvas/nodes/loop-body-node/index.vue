<script setup lang="ts">
import { inject, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue'
import { cloneDeep, set } from 'lodash'
import LogicFlow from '@logicflow/core'
import { SelectionSelect } from '@logicflow/extension'
import type { BaseNodeModel, GraphModel } from '@logicflow/core'
import LoopBodyContainer from './LoopBodyContainer.vue'
import Dagre from '@/workflow-canvas/plugins/dagre'
import AppEdge from '@/workflow-canvas/core/edge/index'
import LoopEdge from '@/workflow-canvas/core/edge/loop-edge'
import { initDefaultShortcut } from '@/workflow-canvas/core/shortcut'
import { disconnectByFlow } from '@/workflow-canvas/core/teleport'
import { KnowledgeWorkFlowInstance, WorkFlowInstance } from '@/workflow-canvas/core/validate'
import { WorkflowMode, type ShapeItem } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowLoopBodyNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

const parentLoopWorkflowMode = inject<WorkflowMode>('loopWorkflowMode') || WorkflowMode.ApplicationLoop
const apiType = (inject('apiType') as string) || 'workspace'
const currentResource = inject<unknown>('currentResource')
const selectModelList = inject<(params: { model_type: string }) => unknown>('getSelectModelList')
const modelParamsForm = inject<(modelId: string) => unknown>('getModelParamsForm')

const containerRef = useTemplateRef<HTMLDivElement>('containerRef')
const lf = shallowRef<LogicFlow | null>(null)

const nodeModules = import.meta.glob<{ default: LogicFlow.RegisterConfig }>('../*/index.ts', { eager: true })

function nestedStartDrag(shapeItem: ShapeItem, event?: PointerEvent) {
  const lfInstance = lf.value
  if (!lfInstance) return
  if (shapeItem.type) {
    lfInstance.dnd.startDrag({ type: shapeItem.type as string, properties: cloneDeep(shapeItem.properties ?? {}) })
    if (event) {
      const containerRect = lfInstance.container.getBoundingClientRect()
      const isInsideCanvas =
        event.clientX >= containerRect.left &&
        event.clientX <= containerRect.right &&
        event.clientY >= containerRect.top &&
        event.clientY <= containerRect.bottom
      if (isInsideCanvas) lfInstance.dnd.dragEnter(event)
    }
  }
  shapeItem.callback?.(lfInstance)
}

const setLoopBody = () => {
  const loopNode = model.graphModel.getNodeModelById(String(model.properties.loop_node_id))
  if (loopNode) {
    if (!loopNode.properties.node_data) set(loopNode.properties, 'node_data', { loop_type: 'ARRAY', array: [], number: 1 })
    loopNode.properties.node_data.loop = { x: model.x, y: model.y }
    loopNode.properties.node_data.loop_body = lf.value?.getGraphData()
  }
}

const validate = () => {
  const lfInstance = lf.value
  if (!lfInstance) return Promise.resolve({})
  const graphData = (lfInstance.getGraphData() ?? { nodes: [], edges: [] }) as unknown as ConstructorParameters<typeof WorkFlowInstance>[0]
  const workflow =
    parentLoopWorkflowMode === WorkflowMode.KnowledgeLoop
      ? new KnowledgeWorkFlowInstance(graphData, parentLoopWorkflowMode)
      : new WorkFlowInstance(graphData, parentLoopWorkflowMode)

  return Promise.all(lfInstance.graphModel.nodes.map((element) => (element as { validate?: () => Promise<unknown> }).validate?.()))
    .then(() => {
      const loopNode = model.graphModel.getNodeModelById(String(model.properties.loop_node_id))
      try {
        workflow.is_loop_valid()
        const nodeData = loopNode?.properties.node_data as { loop_type?: string } | undefined
        if (nodeData?.loop_type === 'LOOP' && !workflow.exist_break_node()) {
          return Promise.reject({ node: loopNode, errMessage: '循环节点需要包含Break节点' })
        }
        return Promise.resolve({})
      } catch (error) {
        return Promise.reject({ node: loopNode, errMessage: error })
      }
    })
    .catch((error) => {
      model.graphModel.selectNodeById(model.id)
      model.graphModel.transformModel.focusOn(model.x, model.y, model.width, model.height)
      throw error
    })
}

const loopLayout = () => {
  const extension = lf.value?.extension as { dagre?: { layout?: () => unknown } } | undefined
  extension?.dagre?.layout?.()
}

const renderGraphData = (data?: LogicFlow.GraphConfigData) => {
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
  const lfInstance = lf.value
  lfInstance.setTheme({ bezier: { stroke: '#afafaf', strokeWidth: 1 } })

  // 嵌套画布位于主画布 foreignObject 内，会随主画布缩放/平移而放大。
  // 覆写 HtmlPointToCanvasPoint，把主画布的 scale/translate 乘进去，使鼠标坐标、节点拖动距离、连线位置与真实位置一致。
  const nestedTransform = lfInstance.graphModel.transformModel
  const parentTransform = model.graphModel.transformModel
  lfInstance.graphModel.transformModel.HtmlPointToCanvasPoint = (point: LogicFlow.PointTuple): LogicFlow.PointTuple => {
    let scaleX = nestedTransform.SCALE_X
    let scaleY = nestedTransform.SCALE_Y
    let translateX = nestedTransform.TRANSLATE_X
    let translateY = nestedTransform.TRANSLATE_Y
    const [x, y] = point
    scaleX *= parentTransform.SCALE_X
    scaleY *= parentTransform.SCALE_Y
    translateX *= parentTransform.SCALE_X
    translateY *= parentTransform.SCALE_Y
    return [(x - translateX) / scaleX, (y - translateY) / scaleY]
  }

  initDefaultShortcut(lfInstance, lfInstance.graphModel)
  lfInstance.graphModel.get_provide = (node: LogicFlow.NodeData | null, graph: GraphModel | null) => ({
    getModel: () => node,
    getGraph: () => graph,
    workflowMode: parentLoopWorkflowMode,
    loopWorkflowMode: parentLoopWorkflowMode,
    currentResource,
    apiType,
    getSelectModelList: selectModelList,
    getModelParamsForm: modelParamsForm,
    startDragNode: nestedStartDrag,
  })
  lfInstance.graphModel.refresh_loop_fields = (fields: Array<{ label: string; value: string }>) => {
    const loopNode = model.graphModel.getNodeModelById(String(model.properties.loop_node_id))
    if (loopNode) {
      loopNode.properties.config.fields = fields
      loopNode.clearNextNodeField?.(true)
    }
  }
  lfInstance.graphModel.getUpNodeFieldList = (containSelf: boolean, useCache: boolean) => model.getUpNodeFieldList(containSelf, useCache)
  lfInstance.graphModel.get_parent_nodes = () => model.graphModel.nodes

  lfInstance.batchRegister([...Object.values(nodeModules).map(({ default: node }) => node), AppEdge, LoopEdge])
  lfInstance.setDefaultEdgeType('app-edge')
  lfInstance.graphModel.eventCenter.on('delete_edge', (edgeIds: string[]) => {
    edgeIds.forEach((edgeId) => lfInstance.deleteEdge(edgeId))
  })
  lfInstance.graphModel.eventCenter.on('anchor:drop', (event) => {
    const nodeModel = event.nodeModel as BaseNodeModel
    ;(nodeModel as { clearNextNodeField?: (containSelf: boolean) => void }).clearNextNodeField?.(false)
  })
  lfInstance.render(data ?? {})
}

onMounted(() => {
  renderGraphData(cloneDeep(model.properties.workflow as LogicFlow.GraphConfigData))
  set(model, 'setLoopBody', setLoopBody)
  set(model, 'set_loop_body', setLoopBody)
  set(model, 'validate', validate)
  set(model, 'loopLayout', loopLayout)
})

onUnmounted(() => {
  disconnectByFlow(lf.value?.graphModel.flowId ?? '')
  lf.value = null
})
</script>

<template>
  <LoopBodyContainer :node-model="model" ref="LoopBodyContainerRef">
    <div
      ref="containerRef"
      class="h-full w-full"
      @wheel.stop
      @mousedown.stop
      @click.stop
      @dblclick.stop
      @contextmenu.stop
      @pointerdown.stop
      @keydown.stop
      @keyup.stop
    />
  </LoopBodyContainer>
</template>
