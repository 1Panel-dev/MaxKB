import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
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
          is_required: {
            type: 'boolean',
            description:
              '默认 true。仅对 source=reference 有效：运行时引用取到的值为空（null / 空字符串 / 空数组）会直接中断节点并报错「字段为必填」。' +
              '引用的上游字段在正常情况下可能为空（如可选的提取结果、模型可能不输出、循环变量起始为空、分支未覆盖的字段等）时必须设为 false，让空值在代码里按业务逻辑处理，而不是让节点中断；只有确定上游一定有值时才设 true',
          },
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
      '- is_required 只对 source=reference 的参数有效：引用的上游值运行时为空会直接报错中断节点，不是「代码里判断一下」就能接住的。引用的字段本身可能为空（可选的提取结果、模型可能不输出、循环变量初始为空等）就必须设 is_required=false，代码里按空值正常处理；只有确定上游一定有值才设 true。',
      '- 示例：def main(text: str, limit: int):\\n    return text[:limit]',
      '- 解析模型输出的 JSON 时先去掉 ```json 代码块标记并做容错（解析失败时返回原数据或空结果），不要让代码直接抛错。',
      '- 返回值结构以「下游要求」为准：有下游要求时按它逐字段构造返回值；顶层是数组就 return 一个 list，哪怕只有一条也不能返回单个 dict，也不能返回 {名称: 内容} 这样的字典。',
      '- 结果要给知识库写入（如补标签 tags、关联问题 problem_list、元数据 meta）时：遍历上游文档分段的 paragraph_list（list），逐篇复制后补字段，原字段一律保留，最后 return 整个 list；'
        + 'AI 输出是 {文档名: [...]} 这样的字典时，只用它按 name 查找，不要把它当返回值；'
        + 'tags 为 [{"key": str, "value": str}]（key ≤64 字、value ≤128 字，均不能为空），problem_list 写在每个分段上，为 list[str]。',
      '- 知识库写入的示例：\\ndef main(documents: list, ai_output: str):\\n    import json, re\\n    text = re.sub(r"^```(json)?|```$", "", (ai_output or "").strip(), flags=re.M).strip()\\n'
        + '    try:\\n        tags_by_name = json.loads(text)\\n    except Exception:\\n        tags_by_name = {}\\n    if not isinstance(tags_by_name, dict):\\n        tags_by_name = {}\\n'
        + '    result = []\\n    for document in documents or []:\\n        tags = [t for t in tags_by_name.get(document.get("name"), []) if isinstance(t, dict) and t.get("key") and t.get("value")]\\n'
        + '        result.append({**document, "tags": (document.get("tags") or []) + tags})\\n    return result',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前自定义工具节点：Python 代码与输入参数、是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const code = typeof args.code === 'string' ? args.code : ''
          if (!/^\s*def\s+\w+\s*\(/m.test(code)) return new ErrorResult('code 需要定义一个 Python 函数')
          const inputs = (Array.isArray(args.inputs) ? args.inputs : []) as Array<Record<string, unknown>>
          const names = new Set<string>()
          const inputFieldList = []
          for (const input of inputs) {
            const name = String(input.name ?? '')
            if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) return new ErrorResult(`参数名不合法：${name}`)
            if (names.has(name)) return new ErrorResult(`参数名重复：${name}`)
            names.add(name)
            const type = FIELD_TYPES.includes(String(input.type)) ? String(input.type) : 'string'
            const isRequired = input.is_required !== false
            const field = { name, type, is_required: isRequired, desc: String(input.desc ?? '') }
            if (input.source === 'reference') {
              const reference = argReference(context, name)
              if (!reference && isRequired) return new ErrorResult(`参数 ${name} 为引用来源，需要父节点传入同名入参`)
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
          return finishWithValidate(context)
        },
      },
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
