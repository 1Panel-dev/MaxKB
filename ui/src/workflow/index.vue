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

const graphData = {
  nodes: [
    ...baseNodes,
    {
      id: 'e781559d-e54b-45d8-bcea-d2d426fd58a3',
      type: 'ai-chat-node',
      x: 600,
      y: 560,
      properties: {
        noRender: true,
        stepName: 'AI 对话',
        fields: [{ label: 'AI 回答内容', value: 'answer' }],
        node_data: {
          model_id: '9bdd1ab3-135b-11ef-b688-a8a1595801ab',
          system: '你是问题分类大师',
          prompt:
            "请直接返回所属的问题分类，不要说推理过程。\n用户问题为：{{context['start-node'].question}}\n问题分类是：\n打招呼 \n售前咨询\n售后咨询\n其他咨询",
          dialogue_number: 0
        }
      }
    },
    {
      id: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      type: 'condition-node',
      x: 1140,
      y: 284,
      properties: {
        noRender: true,
        width: 600,
        stepName: '判断器',
        node_data: {
          branch: [
            {
              conditions: [
                {
                  field: ['e781559d-e54b-45d8-bcea-d2d426fd58a3', 'answer'],
                  compare: 'contain',
                  value: '打招呼 '
                }
              ],
              id: '5675',
              type: 'IF',
              condition: 'and'
            },
            {
              conditions: [
                {
                  field: ['e781559d-e54b-45d8-bcea-d2d426fd58a3', 'answer'],
                  compare: 'contain',
                  value: '售前咨询'
                }
              ],
              type: 'ELSE IF 1',
              id: '9947',
              condition: 'and'
            },
            {
              conditions: [
                {
                  field: ['e781559d-e54b-45d8-bcea-d2d426fd58a3', 'answer'],
                  compare: 'contain',
                  value: '售后咨询'
                }
              ],
              type: 'ELSE IF 2',
              id: '5048',
              condition: 'and'
            },
            { conditions: [], id: '6750', type: 'ELSE', condition: 'and' }
          ]
        },
        branch_condition_list: [
          { index: 0, height: 115.778, id: '5675' },
          { index: 1, height: 115.778, id: '9947' },
          { index: 2, height: 115.778, id: '5048' },
          { index: 3, height: 40, id: '6750' }
        ]
      }
    },
    {
      id: 'ec6f5581-fef3-45a1-8be1-6611a8c9ccfc',
      type: 'reply-node',
      x: 1830,
      y: -220,
      properties: {
        noRender: true,
        stepName: '指定回复',
        node_data: {
          reply_type: 'content',
          content: '你好我是ai只能机器人,很高兴为你服务',
          fields: []
        }
      }
    },
    {
      id: '2ac57a56-9150-4f04-a7b9-6390bdaade19',
      type: 'search-dataset-node',
      x: 1810,
      y: 290,
      properties: {
        noRender: true,
        stepName: '知识库检索',
        fields: [
          { label: '段落列表', value: 'paragraph_list' },
          { label: '满足直接回答的段落列表', value: 'is_hit_handling_method_list' },
          { label: '检索结果', value: 'data' },
          { label: '满足直接回答的分段内容', value: 'directly_return' }
        ],
        node_data: {
          dataset_id_list: ['8ba47817-28a1-11ef-90fd-a8a1595801ab'],
          dataset_setting: {
            top_n: 3,
            similarity: 0.6,
            max_paragraph_char_number: 5000,
            search_mode: 'embedding'
          },
          question_reference_address: ['start-node', 'question']
        }
      }
    },
    {
      id: 'bd9dd852-d749-4b42-9b95-80f25b9a606d',
      type: 'ai-chat-node',
      x: 2430,
      y: 310,
      properties: {
        noRender: true,
        stepName: 'AI 对话',
        fields: [{ label: 'AI 回答内容', value: 'answer' }],
        node_data: {
          model_id: '9bdd1ab3-135b-11ef-b688-a8a1595801ab',
          system: '你是售前咨询知识库',
          prompt:
            "已知信息：\n{{context['2ac57a56-9150-4f04-a7b9-6390bdaade19'].data}}\n问题：\n{{context['start-node'].question}}",
          dialogue_number: 0
        }
      }
    },
    {
      id: '1cd54877-bfff-4791-b8f5-08c49f8bdf66',
      type: 'search-dataset-node',
      x: 1770,
      y: 840,
      properties: {
        noRender: true,
        stepName: '知识库检索',
        fields: [
          { label: '段落列表', value: 'paragraph_list' },
          { label: '满足直接回答的段落列表', value: 'is_hit_handling_method_list' },
          { label: '检索结果', value: 'data' },
          { label: '满足直接回答的分段内容', value: 'directly_return' }
        ],
        node_data: {
          dataset_id_list: ['188c3fa1-28a3-11ef-99e8-a8a1595801ab'],
          dataset_setting: {
            top_n: 3,
            similarity: 0.6,
            max_paragraph_char_number: 5000,
            search_mode: 'embedding'
          },
          question_reference_address: ['start-node', 'question']
        }
      }
    },
    {
      id: 'e99869b2-251f-47a7-9966-c54ffb59b381',
      type: 'condition-node',
      x: 2310,
      y: 930,
      properties: {
        noRender: true,
        width: 600,
        stepName: '判断器',
        node_data: {
          branch: [
            {
              conditions: [
                {
                  field: ['1cd54877-bfff-4791-b8f5-08c49f8bdf66', 'is_hit_handling_method_list'],
                  compare: 'ge',
                  value: '1'
                }
              ],
              id: '3014',
              type: 'IF',
              condition: 'and'
            },
            {
              conditions: [
                {
                  field: ['1cd54877-bfff-4791-b8f5-08c49f8bdf66', 'paragraph_list'],
                  compare: 'ge',
                  value: '1'
                }
              ],
              type: 'ELSE IF 1',
              id: '4658',
              condition: 'and'
            },
            { conditions: [], id: '8871', type: 'ELSE', condition: 'and' }
          ]
        },
        branch_condition_list: [
          { index: 0, height: 115.778, id: '3014' },
          { index: 1, height: 115.778, id: '4658' },
          { index: 2, height: 40, id: '8871' }
        ]
      }
    },
    {
      id: '62ab766b-b218-4bea-895f-b7e83614c8b7',
      type: 'reply-node',
      x: 2940,
      y: 530,
      properties: {
        noRender: true,
        stepName: '指定回复',
        node_data: {
          reply_type: 'referencing',
          content: '',
          fields: ['1cd54877-bfff-4791-b8f5-08c49f8bdf66', 'directly_return']
        }
      }
    },
    {
      id: '04837361-30ea-41bd-96bc-768ee58d69d6',
      type: 'ai-chat-node',
      x: 2930,
      y: 1000,
      properties: {
        noRender: true,
        stepName: 'AI 对话',
        fields: [{ label: 'AI 回答内容', value: 'answer' }],
        node_data: {
          model_id: '9bdd1ab3-135b-11ef-b688-a8a1595801ab',
          system: '你是售后工程师',
          prompt:
            "已知信息：\n{{context['1cd54877-bfff-4791-b8f5-08c49f8bdf66'].data}}\n问题：\n{{context['start-node'].question}}",
          dialogue_number: 0
        }
      }
    },
    {
      id: 'fe4d14fd-9aeb-40ad-b7e0-3d88bf1c5933',
      type: 'reply-node',
      x: 2960,
      y: 1470,
      properties: {
        noRender: true,
        stepName: '指定回复',
        node_data: { reply_type: 'content', content: '未找到相关内容', fields: [] }
      }
    },
    {
      id: 'c9b74adb-e219-4d2b-8fd5-ecc2bac8786e',
      type: 'ai-chat-node',
      x: 1740,
      y: 1470,
      properties: {
        noRender: true,
        stepName: 'AI 对话',
        fields: [{ label: 'AI 回答内容', value: 'answer' }],
        node_data: {
          model_id: '9bdd1ab3-135b-11ef-b688-a8a1595801ab',
          system: '',
          prompt: "{{context['start-node'].question}}",
          dialogue_number: 0
        }
      }
    }
  ],
  edges: [
    {
      id: '21096f2c-d89f-4fb3-b12-61484b0686d4',
      type: 'app-edge',
      sourceNodeId: 'start-node',
      targetNodeId: 'e781559d-e54b-45d8-bcea-d2d426fd58a3',
      startPoint: { x: 340, y: 720 },
      endPoint: { x: 440, y: 560 },
      properties: {},
      pointsList: [
        { x: 340, y: 720 },
        { x: 450, y: 720 },
        { x: 330, y: 560 },
        { x: 440, y: 560 }
      ],
      sourceAnchorId: 'start-node_right',
      targetAnchorId: 'e781559d-e54b-45d8-bcea-d2d426fd58a3_left'
    },
    {
      id: '6019001b-f9e8-4081-9538-ef1e717eac7b',
      type: 'app-edge',
      sourceNodeId: 'e781559d-e54b-45d8-bcea-d2d426fd58a3',
      targetNodeId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      startPoint: { x: 760, y: 560 },
      endPoint: { x: 850, y: 284 },
      properties: {},
      pointsList: [
        { x: 760, y: 560 },
        { x: 870, y: 560 },
        { x: 740, y: 284 },
        { x: 850, y: 284 }
      ],
      sourceAnchorId: 'e781559d-e54b-45d8-bcea-d2d426fd58a3_right',
      targetAnchorId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382_left'
    },
    {
      id: '6dba7e71-c14c-427e-b7de-09f3b1064291',
      type: 'app-edge',
      sourceNodeId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      targetNodeId: 'ec6f5581-fef3-45a1-8be1-6611a8c9ccfc',
      startPoint: { x: 1430, y: 127.33350000000002 },
      endPoint: { x: 1670, y: -220 },
      properties: {},
      pointsList: [
        { x: 1430, y: 127.33350000000002 },
        { x: 1540, y: 127.33350000000002 },
        { x: 1560, y: -220 },
        { x: 1670, y: -220 }
      ],
      sourceAnchorId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382_5675_right',
      targetAnchorId: 'ec6f5581-fef3-45a1-8be1-6611a8c9ccfc_left'
    },
    {
      id: '45a83361-1dfe-499e-8407-8c1670386b04',
      type: 'app-edge',
      sourceNodeId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      targetNodeId: '2ac57a56-9150-4f04-a7b9-6390bdaade19',
      startPoint: { x: 1430, y: 251.11150000000004 },
      endPoint: { x: 1650, y: 290 },
      properties: {},
      pointsList: [
        { x: 1430, y: 251.11150000000004 },
        { x: 1540, y: 251.11150000000004 },
        { x: 1540, y: 290 },
        { x: 1650, y: 290 }
      ],
      sourceAnchorId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382_9947_right',
      targetAnchorId: '2ac57a56-9150-4f04-a7b9-6390bdaade19_left'
    },
    {
      id: 'b18a10f9-df1a-415b-b419-cf44229b3345',
      type: 'app-edge',
      sourceNodeId: '2ac57a56-9150-4f04-a7b9-6390bdaade19',
      targetNodeId: 'bd9dd852-d749-4b42-9b95-80f25b9a606d',
      startPoint: { x: 1970, y: 290 },
      endPoint: { x: 2270, y: 310 },
      properties: {},
      pointsList: [
        { x: 1970, y: 290 },
        { x: 2080, y: 290 },
        { x: 2160, y: 310 },
        { x: 2270, y: 310 }
      ],
      sourceAnchorId: '2ac57a56-9150-4f04-a7b9-6390bdaade19_right',
      targetAnchorId: 'bd9dd852-d749-4b42-9b95-80f25b9a606d_left'
    },
    {
      id: 'd9b31737-a480-48e5-84b6-a8556d1d68a5',
      type: 'app-edge',
      sourceNodeId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      targetNodeId: '1cd54877-bfff-4791-b8f5-08c49f8bdf66',
      startPoint: { x: 1430, y: 374.8895 },
      endPoint: { x: 1610, y: 840 },
      properties: {},
      pointsList: [
        { x: 1430, y: 374.8895 },
        { x: 1540, y: 374.8895 },
        { x: 1500, y: 840 },
        { x: 1610, y: 840 }
      ],
      sourceAnchorId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382_5048_right',
      targetAnchorId: '1cd54877-bfff-4791-b8f5-08c49f8bdf66_left'
    },
    {
      id: '32d36445-b2b8-4472-9c86-3a9c147ceea2',
      type: 'app-edge',
      sourceNodeId: '1cd54877-bfff-4791-b8f5-08c49f8bdf66',
      targetNodeId: 'e99869b2-251f-47a7-9966-c54ffb59b381',
      startPoint: { x: 1930, y: 840 },
      endPoint: { x: 2020, y: 930 },
      properties: {},
      pointsList: [
        { x: 1930, y: 840 },
        { x: 2040, y: 840 },
        { x: 1910, y: 930 },
        { x: 2020, y: 930 }
      ],
      sourceAnchorId: '1cd54877-bfff-4791-b8f5-08c49f8bdf66_right',
      targetAnchorId: 'e99869b2-251f-47a7-9966-c54ffb59b381_left'
    },
    {
      id: '98c9014f-0bfc-4595-9c79-48ea785dc6cd',
      type: 'app-edge',
      sourceNodeId: 'e99869b2-251f-47a7-9966-c54ffb59b381',
      targetNodeId: '62ab766b-b218-4bea-895f-b7e83614c8b7',
      startPoint: { x: 2600, y: 835.2225 },
      endPoint: { x: 2780, y: 530 },
      properties: {},
      pointsList: [
        { x: 2600, y: 835.2225 },
        { x: 2710, y: 835.2225 },
        { x: 2670, y: 530 },
        { x: 2780, y: 530 }
      ],
      sourceAnchorId: 'e99869b2-251f-47a7-9966-c54ffb59b381_3014_right',
      targetAnchorId: '62ab766b-b218-4bea-895f-b7e83614c8b7_left'
    },
    {
      id: '57e76e75-5c7f-42cb-a120-cc890243bb17',
      type: 'app-edge',
      sourceNodeId: 'e99869b2-251f-47a7-9966-c54ffb59b381',
      targetNodeId: '04837361-30ea-41bd-96bc-768ee58d69d6',
      startPoint: { x: 2600, y: 959.0005 },
      endPoint: { x: 2770, y: 1000 },
      properties: {},
      pointsList: [
        { x: 2600, y: 959.0005 },
        { x: 2710, y: 959.0005 },
        { x: 2660, y: 1000 },
        { x: 2770, y: 1000 }
      ],
      sourceAnchorId: 'e99869b2-251f-47a7-9966-c54ffb59b381_4658_right',
      targetAnchorId: '04837361-30ea-41bd-96bc-768ee58d69d6_left'
    },
    {
      id: '8becdf8e-243a-482a-bdf6-22e947aa9bd2',
      type: 'app-edge',
      sourceNodeId: 'e99869b2-251f-47a7-9966-c54ffb59b381',
      targetNodeId: 'fe4d14fd-9aeb-40ad-b7e0-3d88bf1c5933',
      startPoint: { x: 2600, y: 1044.8895 },
      endPoint: { x: 2800, y: 1470 },
      properties: {},
      pointsList: [
        { x: 2600, y: 1044.8895 },
        { x: 2710, y: 1044.8895 },
        { x: 2690, y: 1470 },
        { x: 2800, y: 1470 }
      ],
      sourceAnchorId: 'e99869b2-251f-47a7-9966-c54ffb59b381_8871_right',
      targetAnchorId: 'fe4d14fd-9aeb-40ad-b7e0-3d88bf1c5933_left'
    },
    {
      id: 'f0277552-0d5a-4642-838f-989e59afe350',
      type: 'app-edge',
      sourceNodeId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382',
      targetNodeId: 'c9b74adb-e219-4d2b-8fd5-ecc2bac8786e',
      startPoint: { x: 1430, y: 460.7785 },
      endPoint: { x: 1580, y: 1470 },
      properties: {},
      pointsList: [
        { x: 1430, y: 460.7785 },
        { x: 1540, y: 460.7785 },
        { x: 1470, y: 1470 },
        { x: 1580, y: 1470 }
      ],
      sourceAnchorId: 'c94a8bfb-34b0-4b1b-8456-0a164870d382_6750_right',
      targetAnchorId: 'c9b74adb-e219-4d2b-8fd5-ecc2bac8786e_left'
    }
  ]
}

const lf = ref()
const TRANSLATION_DISTANCE = 40
let CHILDREN_TRANSLATION_DISTANCE = 40
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

    lf.value.render(graphData)

    lf.value.graphModel.eventCenter.on('delete_edge', (id_list: Array<string>) => {
      id_list.forEach((id: string) => {
        lf.value.deleteEdge(id)
      })
    })
  }
})
const validate = () => {
  return Promise.all(lf.value.graphModel.nodes.map((element: any) => element?.validate?.()))
}
const getGraphData = () => {
  return JSON.stringify(lf.value.getGraphData())
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
