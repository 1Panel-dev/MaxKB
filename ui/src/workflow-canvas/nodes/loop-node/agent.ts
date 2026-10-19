import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** loop-node（循环）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    array: { type: 'array', description: 'ARRAY 模式遍历的数组', 'x-bind': 'array' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    loop_type: { type: 'string', enum: ['ARRAY', 'NUMBER', 'LOOP'], description: 'ARRAY 遍历入参 array，NUMBER 固定次数，LOOP 无限循环' },
    number: { type: 'number', description: 'NUMBER 时的次数' },
  },
  required: ['loop_type'],
}

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: false }

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'loop-node（循环）配置要点：只配循环本身，循环体由建图 agent 另行搭建。',
      '- loop_type：ARRAY 遍历已绑定入参 array；NUMBER 循环 number 次；LOOP 无限循环（循环体内必须放 Break）。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const loopType = String(args.loop_type)
        if (!['ARRAY', 'NUMBER', 'LOOP'].includes(loopType)) return `loop_type 不合法：${loopType}`
        const array = argReference(context, 'array')
        if (loopType === 'ARRAY' && !array) return 'ARRAY 模式需要父节点传入入参 array，请改用 NUMBER / LOOP 或说明缺少该入参'
        writeNodeProperties(node, {
          node_data: {
            ...readNodeData<Record<string, unknown>>(node),
            loop_type: loopType,
            array: loopType === 'ARRAY' && array ? [...array] : [],
            number: loopType === 'NUMBER' ? Math.max(1, Number(args.number ?? 1)) : 1,
          },
        })
        return null
      }),
    ],
  })
}

export default {
  description:
    '相当于 for：ARRAY 遍历数组、NUMBER 固定次数、LOOP 无限循环（循环体内必须放 Break）。循环体在 lf_id=该循环节点 id 的画布中搭建，' +
    '首节点接 loop-start-node，以 [loop-start-node, item] / [loop-start-node, index] 取当前元素与下标；要遍历的数组常由参数提取的 array 参数产出',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
