<template>
  <div className="workflow-app" id="container"></div>
  <!-- 辅助工具栏 -->
  <Control class="workflow-control" v-if="lf" :lf="lf"></Control>
</template>
<script setup lang="ts">
import LogicFlow from '@logicflow/core'
import { ref, onMounted } from 'vue'
import AppEdge from './common/edge'
import Control from './common/NodeControl.vue'
import { baseNodes } from '@/workflow/common/data'
import '@logicflow/extension/lib/style/index.css'
import '@logicflow/core/dist/style/index.css'
import { ElMessageBox, ElMessage } from 'element-plus'
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
          { label: '检索结果', value: 'data' },
          { label: '满足直接回答的分段内容', value: 'paragraph' }
        ],
        node_data: {
          dataset_id_list: [],
          dataset_setting: {
            top_n: 3,
            similarity: 0.6,
            max_paragraph_char_number: 5000,
            search_mode: 'embedding'
          },
          question_reference_address: []
        }
      }
    },
    {
      id: '34902d3d-a3ff-497f-b8e1-0c34a44d7dd6',
      type: 'condition-node',
      x: 810,
      y: 760,

      properties: {
        height: 200,
        width: 600,
        stepName: '判断器',
        input: [{ key: '输入' }],
        output: [{ key: '9208' }, { key: '1143' }, { key: '输出' }]
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
        output: [{ key: '输出' }],
        node_data: {
          model_id: '',
          system: '',
          prompt:
            '已知信息：\n{data}\n回答要求：\n- 请使用简洁且专业的语言来回答用户的问题。\n- 如果你不知道答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。\n- 避免提及你是从已知信息中获得的知识。\n- 请保证答案与已知信息中描述的一致。\n- 请使用 Markdown 语法优化答案的格式。\n- 已知信息中的图片、链接地址和脚本语言请直接返回。\n- 请使用与问题相同的语言来回答。\n问题：\n{question}',
          dialogue_number: 1
        }
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
        node_data: {
          model_id: '',
          system: '',
          prompt:
            '已知信息：\n{data}\n回答要求：\n- 请使用简洁且专业的语言来回答用户的问题。\n- 如果你不知道答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。\n- 避免提及你是从已知信息中获得的知识。\n- 请保证答案与已知信息中描述的一致。\n- 请使用 Markdown 语法优化答案的格式。\n- 已知信息中的图片、链接地址和脚本语言请直接返回。\n- 请使用与问题相同的语言来回答。\n问题：\n{question}',
          dialogue_number: 1
        }
      }
    },
    {
      id: '0004a9c9-e2fa-40ac-9215-2e1ad04f09c5',
      type: 'ai-chat-node',
      x: 1360,
      y: 1300,
      properties: {
        height: '',
        stepName: 'AI 对话',
        node_data: {
          model_id: '',
          system: '',
          prompt:
            '已知信息：\n{data}\n回答要求：\n- 请使用简洁且专业的语言来回答用户的问题。\n- 如果你不知道答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。\n- 避免提及你是从已知信息中获得的知识。\n- 请保证答案与已知信息中描述的一致。\n- 请使用 Markdown 语法优化答案的格式。\n- 已知信息中的图片、链接地址和脚本语言请直接返回。\n- 请使用与问题相同的语言来回答。\n问题：\n{question}',
          dialogue_number: 1
        }
      }
    },
    {
      id: '30c16d31-3881-48cd-991e-da3f99c45681',
      type: 'reply-node',
      x: 990,
      y: 300,
      properties: {
        height: '',
        stepName: '指定回复',
        input: [{ key: '' }],
        output: [{ key: '' }]
      }
    }
  ],
  edges: []
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
      keyboard: {
        enabled: true,
        shortcuts: [
          {
            keys: ['backspace'],
            callback: (edge: any) => {
              const defaultOptions: Object = {
                showCancelButton: true,
                confirmButtonText: '确定',
                cancelButtonText: '取消'
              }
              const elements = lf.value.getSelectElements(true)
              ElMessageBox.confirm('确定删除改节点？', defaultOptions).then((ok) => {
                const elements = lf.value.getSelectElements(true)
                lf.value.clearSelectElements()
                elements.edges.forEach((edge: any) => {
                  lf.value.deleteEdge(edge.id)
                })
                elements.nodes.forEach((node: any) => {
                  lf.value.deleteNode(node.id)
                })
              })
            }
          },
          {
            keys: ['cmd + c', 'ctrl + c'],
            callback: (edge: any) => {
              ElMessage.success({
                message: '已复制节点',
                type: 'success',
                showClose: true,
                duration: 1500
              })
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
    lf.value.graphModel.eventCenter.on('delete_edge', (id_list: Array<string>) => {
      id_list.forEach((id: string) => {
        lf.value.deleteEdge(id)
      })
    })
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
