<template>
  <div className="workflow-app" id="container"></div>
  <!-- 辅助工具栏 -->
  <Control class="workflow-control" v-if="lf" :lf="lf"></Control>
</template>
<script setup lang="ts">
import LogicFlow from '@logicflow/core'
import { ref, onMounted, computed } from 'vue'
import AppEdge from './common/edge'
import Control from './common/NodeControl.vue'
import { baseNodes } from '@/workflow/common/data'
import '@logicflow/extension/lib/style/index.css'
import '@logicflow/core/dist/style/index.css'
import { initDefaultShortcut } from '@/workflow/common/shortcut'
const nodes: any = import.meta.glob('./nodes/**/index.ts', { eager: true })

defineOptions({ name: 'WorkFlow' })

type ShapeItem = {
  type?: string
  text?: string
  icon?: string
  label?: string
  className?: string
  disabled?: boolean
  properties?: Record<string, any>
  callback?: (lf: LogicFlow, container?: HTMLElement) => void
}

const props = defineProps({
  data: Object || null
})

const defaultData = {
  nodes: [...baseNodes]
}
const graphData = computed({
  get: () => {
    if (props.data) {
      return props.data
    } else {
      return defaultData
    }
  },
  set: (value) => {
    return value
  }
})

const lf = ref()
onMounted(() => {
  const container: any = document.querySelector('#container')
  if (container) {
    lf.value = new LogicFlow({
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

    lf.value.render(graphData.value)

    lf.value.graphModel.eventCenter.on('delete_edge', (id_list: Array<string>) => {
      id_list.forEach((id: string) => {
        lf.value.deleteEdge(id)
      })
    })
    setTimeout(() => {
      lf.value?.fitView()
    }, 500)
  }
})
const validate = () => {
  return Promise.all(lf.value.graphModel.nodes.map((element: any) => element?.validate?.()))
}
const getGraphData = () => {
  return lf.value.getGraphData()
}

const onmousedown = (shapeItem: ShapeItem) => {
  if (shapeItem.type) {
    lf.value.dnd.startDrag({
      type: shapeItem.type,
      properties: { ...shapeItem.properties }
    })
  }
  if (shapeItem.callback) {
    shapeItem.callback(lf.value)
  }
}
const addNode = (shapeItem: ShapeItem) => {
  lf.value.clearSelectElements()
  const { virtualRectCenterPositionX, virtualRectCenterPositionY } =
    lf.value.graphModel.getVirtualRectSize()
  const newNode = lf.value.graphModel.addNode({
    type: shapeItem.type,
    properties: shapeItem.properties,
    x: virtualRectCenterPositionX,
    y: virtualRectCenterPositionY - lf.value.graphModel.height / 2
  })
  newNode.isSelected = true
  newNode.isHovered = true
  lf.value.toFront(newNode.id)
}

const clearGraphData = () => {
  return lf.value.graphModel.clearData()
}

defineExpose({
  onmousedown,
  validate,
  getGraphData,
  addNode,
  clearGraphData
})
</script>
<style lang="scss">
.workflow-app {
  width: 100%;
  height: 100%;
  position: relative;
}
.workflow-control {
  position: absolute;
  bottom: 24px;
  left: 24px;
  z-index: 2;
}
</style>
