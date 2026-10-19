import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { createUpdateTool, getModelsTool, MODEL_FIELD_SCHEMA, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'

const PARAMETER_TYPES = ['string', 'int', 'number', 'boolean', 'array', 'object']

/** parameter-extraction-node（参数提取）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    text: { type: 'string', description: '被提取的文本', 'x-bind': 'input_variable' },
  },
  required: ['text'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    parameters: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string' },
          label: { type: 'string' },
          parameter_type: { type: 'string', enum: PARAMETER_TYPES },
          desc: { type: 'string' },
        },
        required: ['field', 'label', 'parameter_type'],
      },
      description: '要提取的参数：field 英文名，label 中文名，parameter_type 类型，desc 提取规则',
    },
  },
  required: ['model', 'parameters'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'object', description: '全部提取结果（参数名 → 值）' },
  },
  additionalProperties: {
    description: '每个提取参数一个返回字段：字段名为 config.parameters[].field，类型为其 parameter_type',
    'x-from': 'parameters',
  },
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'parameter-extraction-node（参数提取）配置要点：',
      '- model：已配置默认模型时传 "default"，否则 get_models 选 id。',
      '- 被提取的文本已由入参 text 绑定，无需配置。',
      '- parameters：要提取的参数，field 英文名，label 中文名，parameter_type 取 string/int/number/boolean/array/object，desc 写清提取规则。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const modelFields = resolveModelFields(context, args.model)
        if (typeof modelFields === 'string') return modelFields
        const parameters = (Array.isArray(args.parameters) ? args.parameters : []) as Array<Record<string, string>>
        if (!parameters.length) return 'parameters 至少一个参数'
        for (const parameter of parameters) {
          if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(String(parameter.field))) return `参数名不合法：${parameter.field}`
          if (!PARAMETER_TYPES.includes(parameter.parameter_type ?? '')) return `参数类型不合法：${parameter.parameter_type}`
        }
        const variableList = parameters.map((parameter) => ({
          field: parameter.field,
          label: parameter.label,
          parameter_type: parameter.parameter_type,
          desc: parameter.desc ?? '',
        }))
        writeNodeProperties(node, {
          node_data: {
            ...readNodeData<Record<string, unknown>>(node),
            ...modelFields,
            variable_list: variableList,
          },
          config: {
            ...(node.properties.config as Record<string, unknown>),
            fields: [{ label: '结果', value: 'result' }, ...variableList.map((parameter) => ({ label: parameter.label, value: parameter.field }))],
          },
        })
        node.clearNextNodeField(true)
        return null
      }),
      getModelsTool(context),
    ],
  })
}

export default {
  description: '用大模型把文本解析成结构化参数；提取出的 array 参数可交给循环遍历，其余参数供下游提示词或判断器使用',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
