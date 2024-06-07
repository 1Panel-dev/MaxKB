<template>
  <div className="workflow-app" id="container"></div>
  <!-- 辅助工具栏 -->
  <Control class="workflow-control" v-if="lf" :lf="lf"></Control>
</template>
<script setup lang="ts">
import LogicFlow from '@logicflow/core'
import { ref, onMounted } from 'vue'
import AppEdge from './common/edge.ts'
import Control from './common/NodeControl.vue'
import { baseNodes } from '@/workflow/common/data.ts'
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
  callback?: (lf: LogicFlow, container?: HTMLElement) => void
}

const graphData = {
  nodes: [
    ...baseNodes,
    {
      id: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd5',
      type: 'search-dataset-node',
      x: 600,
      y: 250,
      properties: {
        height: 200,
        stepName: '知识库检索',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }],
        fields: [
          {
            label: '检索结果',
            value: 'data'
          },
          {
            label: '满足直接回答的分段内容',
            value: 'paragraph'
          }
        ],
        node_data: {
          dataset_id_list: [],
          dataset_setting: {
            top_n: 3,
            similarity: 0.6,
            max_paragraph_char_number: 5000,
            search_mode: 'embedding'
          }
        }
      }
    },
    {
      id: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      type: 'condition-node',
      x: 810,
      y: 764,
      properties: {
        height: 200,
        width: 600,
        stepName: '判断器',
        input: [{ key: '输入' }],
        output: [{ key: '9208' }, { key: '1143' }, { key: '输出' }],
        node_data: {
          branch: [
            {
              conditions: [{ field: [], compare: '', value: '' }],
              id: '2391',
              condition: 'and'
            },
            {
              conditions: [{ field: [], compare: '', value: '' }],
              id: '1143',
              condition: 'and'
            },
            {
              conditions: [{ field: [], compare: '', value: '' }],
              id: '9208',
              condition: 'and'
            }
          ]
        }
      }
    },
    {
      id: '03597cb0-ed4c-4bcb-b25b-3b358f72b266',
      type: 'ai-chat-node',
      x: 1330,
      y: 690,
      properties: {
        height: '',
        stepName: 'AI 对话',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }]
      }
    },
    {
      id: '6649ee86-348c-4d68-9cad-71f0612beb05',
      type: 'ai-chat-node',
      x: 1320,
      y: 990,
      properties: {
        height: '',
        stepName: 'AI 对话',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }]
      }
    },
    {
      id: 'ede4a9c9-e2fa-40ac-9215-2e1ad04f09c5',
      type: 'ai-chat-node',
      x: 1360,
      y: 1300,
      properties: {
        height: '',
        stepName: 'AI 对话',
        input: [{ key: '输入' }],
        output: [{ key: '输出' }]
      }
    }
  ],
  edges: [
    {
      id: '8dde4baf-0965-4999-9d37-f867ab16d638',
      type: 'app-edge',
      sourceNodeId: 'start-node',
      targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd5',
      startPoint: { x: 340, y: 788 },
      endPoint: { x: 440, y: 469 },
      properties: {},
      pointsList: [
        { x: 340, y: 788 },
        { x: 450, y: 788 },
        { x: 330, y: 469 },
        { x: 440, y: 469 }
      ],
      sourceAnchorId: 'start-node_输出_right',
      targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd5_输入_left'
    },
    {
      id: 'b60de7b4-d8d2-4e7d-bba6-3738b9e523b9',
      type: 'app-edge',
      sourceNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd5',
      targetNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      startPoint: { x: 760, y: 464 },
      endPoint: { x: 520, y: 973.75 },
      properties: {},
      pointsList: [
        { x: 760, y: 464 },
        { x: 870, y: 464 },
        { x: 410, y: 973.75 },
        { x: 520, y: 973.75 }
      ],
      sourceAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd5_输出_right',
      targetAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_输入_left'
    },
    {
      id: '8de0da85-b5d6-459a-8be9-4d00082baf1c',
      type: 'app-edge',
      sourceNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      targetNodeId: '03597cb0-ed4c-4bcb-b25b-3b358f72b266',
      startPoint: { x: 1100, y: 968.75 },
      endPoint: { x: 1170, y: 803 },
      properties: {},
      pointsList: [
        { x: 1100, y: 968.75 },
        { x: 1210, y: 968.75 },
        { x: 1060, y: 803 },
        { x: 1170, y: 803 }
      ],
      sourceAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_9208_right',
      targetAnchorId: '03597cb0-ed4c-4bcb-b25b-3b358f72b266_输入_left'
    },
    {
      id: '3e66821a-ce0a-4ef9-a6cf-ea4095158261',
      type: 'app-edge',
      sourceNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      targetNodeId: '6649ee86-348c-4d68-9cad-71f0612beb05',
      startPoint: { x: 1100, y: 992.75 },
      endPoint: { x: 1160, y: 1103 },
      properties: {},
      pointsList: [
        { x: 1100, y: 992.75 },
        { x: 1210, y: 992.75 },
        { x: 1050, y: 1103 },
        { x: 1160, y: 1103 }
      ],
      sourceAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_1143_right',
      targetAnchorId: '6649ee86-348c-4d68-9cad-71f0612beb05_输入_left'
    },
    {
      id: 'cc52ab90-58e7-4f54-9660-d9fb16f776ea',
      type: 'app-edge',
      sourceNodeId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      targetNodeId: 'ede4a9c9-e2fa-40ac-9215-2e1ad04f09c5',
      startPoint: { x: 1100, y: 1016.75 },
      endPoint: { x: 1200, y: 1413 },
      properties: {},
      pointsList: [
        { x: 1100, y: 1016.75 },
        { x: 1210, y: 1016.75 },
        { x: 1090, y: 1413 },
        { x: 1200, y: 1413 }
      ],
      sourceAnchorId: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_输出_right',
      targetAnchorId: 'ede4a9c9-e2fa-40ac-9215-2e1ad04f09c5_输入_left'
    }
  ]
}
const lf = ref()

onMounted(() => {
  const container: any = document.querySelector('#container')
  if (container) {
    lf.value = new LogicFlow({
      textEdit: false,
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
      // keyboard: {
      //   enabled: true,
      //   shortcuts: [
      //     {
      //       keys: ['backspace'],
      //       callback: () => {
      //         const elements = lf.value.getSelectElements(true)
      //         if (
      //           (elements.edges && elements.edges.length > 0) ||
      //           (elements.nodes && elements.nodes.length > 0)
      //         ) {
      //           const r = window.confirm('确定要删除吗？')
      //           if (r) {
      //             lf.value.clearSelectElements()
      //             elements.edges.forEach((edge: any) => {
      //               lf.value.deleteEdge(edge.id)
      //             })
      //             elements.nodes.forEach((node: any) => {
      //               lf.value.deleteNode(node.id)
      //             })
      //           }
      //         }
      //       }
      //     }
      //   ]
      // },
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
  }
})
const validate = () => {
  lf.value.graphModel.nodes.forEach((element: any) => {
    element?.validate?.()
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
  onmousedown,
  validate,
  getGraphData
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
// .lf-dnd-text {
//   width: 200px;
// }
// .lf-dnd-shape {
//   height: 50px;
// }
// .lf-node-selected {
//   border: 1px solid #000;
// }
</style>
