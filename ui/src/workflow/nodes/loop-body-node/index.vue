<template>
  <LoopBodyContainer :nodeModel="nodeModel">
    <div ref="containerRef" @wheel.stop style="height: 100%; width: 100%"></div>
  </LoopBodyContainer>
</template>
<script setup lang="ts">
import { set, cloneDeep } from 'lodash'
import AppEdge from '@/workflow/common/edge'
import { ref, onMounted, onUnmounted } from 'vue'
import LogicFlow from '@logicflow/core'
import Dagre from '@/workflow/plugins/dagre'
import { initDefaultShortcut } from '@/workflow/common/shortcut'
import LoopBodyContainer from '@/workflow/nodes/loop-body-node/LoopBodyContainer.vue'
import { WorkflowMode } from '@/enums/application'
import { WorkFlowInstance } from '@/workflow/common/validate'
import { t } from '@/locales'
import { disconnectByFlow } from '@/workflow/common/teleport'
const nodes: any = import.meta.glob('@/workflow/nodes/**/index.ts', { eager: true })
const props = defineProps<{ nodeModel: any }>()
const containerRef = ref()

const validate = () => {
  const workflow = new WorkFlowInstance(lf.value.getGraphData(), WorkflowMode.ApplicationLoop)
  return Promise.all(lf.value.graphModel.nodes.map((element: any) => element?.validate?.()))
    .then(() => {
      const loop_node_id = props.nodeModel.properties.loop_node_id
      const loop_node = props.nodeModel.graphModel.getNodeModelById(loop_node_id)
      try {
        workflow.is_loop_valid()
        if (loop_node.properties.node_data.loop_type == 'LOOP' && !workflow.exist_break_node()) {
          return Promise.reject({
            node: loop_node,
            errMessage: t('views.applicationWorkflow.validate.loopNodeBreakNodeRequired'),
          })
        }

        return Promise.resolve({})
      } catch (e) {
        return Promise.reject({ node: loop_node, errMessage: e })
      }
    })
    .catch((e) => {
      props.nodeModel.graphModel.selectNodeById(props.nodeModel.id)
      props.nodeModel.graphModel.transformModel.focusOn(
        props.nodeModel.x,
        props.nodeModel.y,
        props.nodeModel.width,
        props.nodeModel.height,
      )
      throw e
    })
}
const set_loop_body = () => {
  const loop_node_id = props.nodeModel.properties.loop_node_id
  const loop_node = props.nodeModel.graphModel.getNodeModelById(loop_node_id)
  loop_node.properties.node_data.loop = {
    x: props.nodeModel.x,
    y: props.nodeModel.y,
  }
  loop_node.properties.node_data.loop_body = lf.value.getGraphData()
}

const refresh_loop_fields = (fields: Array<any>) => {
  const loop_node_id = props.nodeModel.properties.loop_node_id
  const loop_node = props.nodeModel.graphModel.getNodeModelById(loop_node_id)
  if (loop_node) {
    loop_node.properties.config.fields = fields
  }
}

const lf = ref()

const renderGraphData = (data?: any) => {
  const container: any = containerRef.value
  if (container) {
    lf.value = new LogicFlow({
      plugins: [Dagre],
      textEdit: false,
      adjustEdge: false,
      adjustEdgeStartAndEnd: false,
      background: {
        backgroundColor: '#f5f6f7',
      },
      grid: {
        size: 10,
        type: 'dot',
        config: {
          color: '#DEE0E3',
          thickness: 1,
        },
      },
      keyboard: {
        enabled: true,
      },
      isSilentMode: false,
      container: container,
    })
    lf.value.setTheme({
      bezier: {
        stroke: '#afafaf',
        strokeWidth: 1,
      },
    })

    function HtmlPointToCanvasPoint(point: any) {
      let scaleX = lf.value.graphModel.transformModel.SCALE_X as number
      let scaleY = lf.value.graphModel.transformModel.SCALE_Y as number
      let translateX = lf.value.graphModel.transformModel.TRANSLATE_X
      let translateY = lf.value.graphModel.transformModel.TRANSLATE_Y
      const [x, y] = point
      props.nodeModel.graphModel.transformModel
      scaleX *= props.nodeModel.graphModel.transformModel.SCALE_X
      scaleY *= props.nodeModel.graphModel.transformModel.SCALE_Y
      translateX *= props.nodeModel.graphModel.transformModel.SCALE_X
      translateY *= props.nodeModel.graphModel.transformModel.SCALE_Y
      return [(x - translateX) / scaleX, (y - translateY) / scaleY]
    }

    lf.value.graphModel.transformModel.HtmlPointToCanvasPoint = HtmlPointToCanvasPoint.bind(
      lf.value.graphModel.transformModel,
    )

    initDefaultShortcut(lf.value, lf.value.graphModel)
    lf.value.graphModel.get_provide = (node: any, graph: any) => {
      return {
        getNode: () => node,
        getGraph: () => graph,
        workflowMode: WorkflowMode.ApplicationLoop,
      }
    }
    lf.value.graphModel.refresh_loop_fields = refresh_loop_fields
    lf.value.graphModel.get_parent_nodes = () => {
      return props.nodeModel.graphModel.nodes
    }
    lf.value.graphModel.get_up_node_field_list = props.nodeModel.get_up_node_field_list
    lf.value.batchRegister([...Object.keys(nodes).map((key) => nodes[key].default), AppEdge])
    lf.value.setDefaultEdgeType('app-edge')
    lf.value.render(data ? data : {})

    lf.value.graphModel.eventCenter.on('delete_edge', (id_list: Array<string>) => {
      id_list.forEach((id: string) => {
        lf.value.deleteEdge(id)
      })
    })
    lf.value.graphModel.eventCenter.on('anchor:drop', (data: any) => {
      // 清除当前节点下面的子节点的所有缓存
      data.nodeModel.clear_next_node_field(false)
    })
    lf.value.graphModel.eventCenter.on('anchor:drop', (data: any) => {
      // 清除当前节点下面的子节点的所有缓存
      data.nodeModel.clear_next_node_field(false)
    })

    setTimeout(() => {
      lf.value?.fitView()
    }, 500)
  }
}
onMounted(() => {
  renderGraphData(cloneDeep(props.nodeModel.properties.workflow))
  set(props.nodeModel, 'validate', validate)
  set(props.nodeModel, 'set_loop_body', set_loop_body)
})
onUnmounted(() => {
  disconnectByFlow(lf.value.graphModel.flowId)
  lf.value = null
})
</script>
<style lang="scss" scoped></style>
