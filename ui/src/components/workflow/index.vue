<template>
  <button @click="validate">点击校验</button>
  <button @click="getGraphData">点击获取流程数据</button>
  <div className="helloworld-app sql" style="height: 100vh; width: 100vw" id="container"></div>
</template>
<script setup lang="ts">
import LogicFlow from '@logicflow/core'
import { ref, onMounted } from 'vue'
import AiChatNode from '@/workflow/nodes/ai-chat-node/index.ts'
import AppEdge from '@/workflow/common/edge/index'
import { AppMenu } from '@/workflow/common/menu/index'
import '@logicflow/extension/lib/style/index.css'
import '@logicflow/core/dist/style/index.css'

LogicFlow.use(AppMenu)

const graphData = {
  nodes: [
    {
      id: '92a94b25-453d-4a00-aa26-9fed9b487e08',
      type: 'ai-chat-node',
      x: -10,
      y: 239,
      properties: {
        height: 200,
        stepName: 'AI对话',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }],
        node_data: { model: 'shanghai', name: '222' }
      }
    },
    {
      id: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
      type: 'ai-chat-node',
      x: 143,
      y: 523,
      properties: {
        height: 200,
        stepName: 'AI对话',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }],
        node_data: { model: 'shanghai', name: '222222' }
      }
    }
  ],
  edges: [
    {
      id: 'bc7297fa-2409-4c85-9a4d-3d74c9c1e30f',
      type: 'app-edge',
      sourceNodeId: '92a94b25-453d-4a00-aa26-9fed9b487e08',
      targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
      startPoint: { x: 230, y: 333.000005 },
      endPoint: { x: -97, y: 596.111105 },
      properties: {},
      pointsList: [
        { x: 230, y: 333.000005 },
        { x: 340, y: 333.000005 },
        { x: -207, y: 596.111105 },
        { x: -97, y: 596.111105 }
      ],
      sourceAnchorId: '92a94b25-453d-4a00-aa26-9fed9b487e08_输出_right',
      targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4_输入_left'
    },
    {
      id: '9f5740ce-b55e-42d4-90a2-a06f34d6f5ef',
      type: 'app-edge',
      sourceNodeId: '92a94b25-453d-4a00-aa26-9fed9b487e08',
      targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4',
      startPoint: { x: 230, y: 333.000005 },
      endPoint: { x: -97, y: 596.111105 },
      properties: {},
      pointsList: [
        { x: 230, y: 333.000005 },
        { x: 340, y: 333.000005 },
        { x: -207, y: 596.111105 },
        { x: -97, y: 596.111105 }
      ],
      sourceAnchorId: '92a94b25-453d-4a00-aa26-9fed9b487e08_输出_right',
      targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd4_输入_left'
    }
  ]
}
const lf = ref()

onMounted(() => {
  const container: any = document.querySelector('#container')
  if (container) {
    lf.value = new LogicFlow({
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

    lf.value.register(AiChatNode)
    lf.value.register(AppEdge)
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
