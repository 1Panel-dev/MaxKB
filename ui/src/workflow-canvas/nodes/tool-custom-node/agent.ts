import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** tool-custom-node（自定义工具）的 AI 生成配置：生成 Python 代码与输入参数 */

const FIELD_TYPES = ['string', 'int', 'float', 'dict', 'array']

const params: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: { type: 'any', description: 'source=reference 的输入参数，键为参数名（config.inputs[].name）' },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    code: {
      type: 'string',
      description: 'Python 代码：定义一个函数，形参与 inputs 的 name 一一对应，返回值即节点结果；最后定义的函数被调用',
    },
    inputs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string', description: '参数名，与函数形参一致' },
          type: { type: 'string', enum: FIELD_TYPES },
          source: { type: 'string', enum: ['reference', 'custom'], description: 'reference 由同名入参引用上游，custom 为常量' },
          is_required: { type: 'boolean', description: '是否必填，默认 true' },
          desc: { type: 'string', description: '参数说明' },
          value: { description: 'source=custom 时的常量值' },
        },
        required: ['name', 'type', 'source'],
      },
      description: '输入参数：name 参数名，type 类型，source 来源（reference 引用上游 / custom 常量）',
    },
    is_result: { type: 'boolean', description: '是否把结果输出给用户，默认 false' },
  },
  required: ['code', 'inputs'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'any', description: '代码函数的返回值' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'tool-custom-node（自定义工具）配置要点：',
      '- code：按需求写一段可直接运行的 Python，只定义一个函数，形参与 inputs 的 name 一一对应，return 结果；只用标准库。',
      '- inputs：source=reference 的参数由同名入参绑定，无需给 value；source=custom 的参数给常量 value。',
      '- 示例：def main(text: str, limit: int):\\n    return text[:limit]',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const code = typeof args.code === 'string' ? args.code : ''
        if (!/^\s*def\s+\w+\s*\(/m.test(code)) return 'code 需要定义一个 Python 函数'
        const inputs = (Array.isArray(args.inputs) ? args.inputs : []) as Array<Record<string, unknown>>
        const names = new Set<string>()
        const inputFieldList = []
        for (const input of inputs) {
          const name = String(input.name ?? '')
          if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) return `参数名不合法：${name}`
          if (names.has(name)) return `参数名重复：${name}`
          names.add(name)
          const type = FIELD_TYPES.includes(String(input.type)) ? String(input.type) : 'string'
          const isRequired = input.is_required !== false
          const field = { name, type, is_required: isRequired, desc: String(input.desc ?? '') }
          if (input.source === 'reference') {
            const reference = argReference(context, name)
            if (!reference && isRequired) return `参数 ${name} 为引用来源，需要父节点传入同名入参`
            inputFieldList.push({ ...field, source: 'reference', value: reference ? [...reference] : [] })
          } else {
            const value = input.value
            inputFieldList.push({ ...field, source: 'custom', value: value === undefined ? '' : typeof value === 'string' ? value : JSON.stringify(value) })
          }
        }
        const nodeData = readNodeData<Record<string, unknown>>(node)
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            code,
            input_field_list: inputFieldList,
            is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? false),
          },
        })
        return null
      }),
    ],
  })
}

export default {
  description: '执行一段 Python 代码处理数据（格式转换、计算、拼接、规则判断等模型不擅长的确定性逻辑），返回值为结果；入参为代码中引用上游的参数',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
