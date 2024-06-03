<template>
  <!-- <button @click="validate">点击校验</button>
  <button @click="getGraphData">点击获取流程数据</button> -->
  <div className="helloworld-app sql" style="height: 100%; width: 100%" id="container"></div>
</template>
<script setup lang="ts">
import LogicFlow from '@logicflow/core'
import { ref, onMounted } from 'vue'
import AppEdge from './common/edge/index'
import { AppMenu } from './common/menu/index'
import '@logicflow/extension/lib/style/index.css'
import '@logicflow/core/dist/style/index.css'
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
  callback?: (lf: LogicFlow, container: HTMLElement) => void
}
// LogicFlow.use(AppMenu)

const graphData = {
  nodes: [
    {
      id: '92a94b25-453d-4a00-aa26-9fed9b487e08',
      type: 'base-node',
      x: 0,
      y: 250,
      properties: {
        height: 200,
        stepName: '基本信息',
        // input: [{ key: '输入' }],
        // output: [{ key: '输出' }],
        node_data: {
          name: '2222',
          desc: '',
          prologue:
            '您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。\n- MaxKB 主要功能有什么？\n- MaxKB 支持哪些大语言模型？\n- MaxKB 支持哪些文档类型？'
        }
      }
    },
    {
      id: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
      type: 'start-node',
      x: 0,
      y: 753,
      properties: {
        height: 200,
        stepName: '开始',
        // input: [{ key: '输入' }],
        output: [{ key: '输出' }]
        // node_data: { model: 'shanghai', name: '222222' }
      }
    }
  ]
  // edges: [
  //   {
  //     id: 'bc7297fa-2409-4c85-9a4d-3d74c9c1e30f',
  //     type: 'app-edge',
  //     sourceNodeId: '92a94b25-453d-4a00-aa26-9fed9b487e08',
  //     targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
  //     startPoint: { x: 230, y: 333.000005 },
  //     endPoint: { x: -97, y: 596.111105 },
  //     properties: {},
  //     pointsList: [
  //       { x: 230, y: 333.000005 },
  //       { x: 340, y: 333.000005 },
  //       { x: -207, y: 596.111105 },
  //       { x: -97, y: 596.111105 }
  //     ],
  //     sourceAnchorId: '92a94b25-453d-4a00-aa26-9fed9b487e08_输出_right',
  //     targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4_输入_left'
  //   },
  //   {
  //     id: '9f5740ce-b55e-42d4-90a2-a06f34d6f5ef',
  //     type: 'app-edge',
  //     sourceNodeId: '92a94b25-453d-4a00-aa26-9fed9b487e08',
  //     targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
  //     startPoint: { x: 230, y: 333.000005 },
  //     endPoint: { x: -97, y: 596.111105 },
  //     properties: {},
  //     pointsList: [
  //       { x: 230, y: 333.000005 },
  //       { x: 340, y: 333.000005 },
  //       { x: -207, y: 596.111105 },
  //       { x: -97, y: 596.111105 }
  //     ],
  //     sourceAnchorId: '92a94b25-453d-4a00-aa26-9fed9b487e08_输出_right',
  //     targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4_输入_left'
  //   }
  // ]
}
const lf = ref()

onMounted(() => {
  const container: any = document.querySelector('#container')
  if (container) {
    lf.value = new LogicFlow({
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
        enabled: true,
        shortcuts: [
          {
            keys: ['backspace'],
            callback: () => {
              const elements = lf.value.getSelectElements(true)
              if (
                (elements.edges && elements.edges.length > 0) ||
                (elements.nodes && elements.nodes.length > 0)
              ) {
                const r = window.confirm('确定要删除吗？')
                if (r) {
                  lf.value.clearSelectElements()
                  elements.edges.forEach((edge: any) => {
                    lf.value.deleteEdge(edge.id)
                  })
                  elements.nodes.forEach((node: any) => {
                    lf.value.deleteNode(node.id)
                  })
                }
              }
            }
          }
        ]
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

    lf.value.batchRegister([...Object.keys(nodes).map((key) => nodes[key].default), AppEdge])
    lf.value.setDefaultEdgeType('app-edge')

    lf.value.render(graphData)

    lf.value.translateCenter()
  }
})
const validate = () => {
  lf.value.graphModel.nodes.forEach((element: any) => {
    element.validate()
  })
}
const getGraphData = () => {
  console.log(JSON.stringify(lf.value.getGraphData()))
}

const onmousedown = (shapeItem: ShapeItem) => {
  if (shapeItem.type) {
    lf.value.dnd.startDrag({
      type: shapeItem.type,
      properties: shapeItem.properties,
      icon: shapeItem.icon
    })
  }
  if (shapeItem.callback) {
    shapeItem.callback(lf.value)
  }
}

defineExpose({
  onmousedown
})
</script>
<style lang="scss">
.lf-dnd-text {
  width: 200px;
}
.lf-dnd-shape {
  height: 50px;
}
.lf-node-selected {
  border: 1px solid #000;
}
</style>
