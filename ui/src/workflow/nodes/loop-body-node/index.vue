<template>
  <LoopBodyContainer :nodeModel="nodeModel">
    <div ref="containerRef" @wheel.stop style="height: 550px"></div>
  </LoopBodyContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import AppEdge from '@/workflow/common/edge'
import { ref, onMounted } from 'vue'
import LogicFlow from '@logicflow/core'
import Dagre from '@/workflow/plugins/dagre'
import { initDefaultShortcut } from '@/workflow/common/shortcut'
import LoopBodyContainer from '@/workflow/nodes/loop-body-node/LoopBodyContainer.vue'

const nodes: any = import.meta.glob('@/workflow/nodes/**/index.ts', { eager: true })
const props = defineProps<{ nodeModel: any }>()
const containerRef = ref()

const validate = () => {
  return Promise.all(lf.value.graphModel.nodes.map((element: any) => element?.validate?.()))
}
const set_loop_body = () => {
  const loop_node_id = props.nodeModel.properties.loop_node_id
  const loop_node = props.nodeModel.graphModel.getNodeModelById(loop_node_id)
  loop_node.properties.node_data.loop_body = lf.value.getGraphData()
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
        backgroundColor: '#f5f6f7'
      },
      grid: {
        size: 10,
        type: 'dot',
        config: {
          color: '#DEE0E3',
          thickness: 1
        }
      },
      keyboard: {
        enabled: true
      },
      isSilentMode: false,
      container: container
    })
    lf.value.setTheme({
      bezier: {
        stroke: '#afafaf',
        strokeWidth: 1
      }
    })

    initDefaultShortcut(lf.value, lf.value.graphModel)
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
    lf.value.graphModel.eventCenter.on('history:change', (data: any) => {
      set(props.nodeModel.properties, 'workflow', lf.value.getGraphData())
    })
    setTimeout(() => {
      lf.value?.fitView()
    }, 500)
  }
}
onMounted(() => {
  renderGraphData(props.nodeModel.properties.workflow)
  set(props.nodeModel, 'validate', validate)
  set(props.nodeModel, 'set_loop_body', set_loop_body)
})
</script>
<style lang="scss" scoped></style>
