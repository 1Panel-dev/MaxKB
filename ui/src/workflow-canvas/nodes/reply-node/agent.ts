import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** reply-node（指定回复）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    value: { type: 'any', description: '直接输出的上游变量（reply_type=referencing 时必传）' },
    materials: { type: 'array', items: {}, description: '回复文本里要内嵌的上游变量（reply_type=content 时可选）' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    reply_type: { type: 'string', enum: ['content', 'referencing'], description: 'content 输出文本，referencing 直接输出入参 value' },
    content_type: { type: 'string', enum: ['TEXT', 'HTML', 'TOOL'], description: '回复内容格式（reply_type=content 时）：TEXT 文本，HTML 富文本，TOOL 工具调用结果 JSON' },
    content: { type: 'string', description: 'reply_type=content 时的回复文本，可内嵌入参 materials 的 {{节点名称.字段}}' },
    is_result: { type: 'boolean', description: '是否输出给用户，默认 true' },
  },
  required: ['reply_type'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    answer: { type: 'string', description: '输出的内容' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'reply-node（指定回复）配置要点：',
      '- reply_type="content"：输出 content 文本，可内嵌已绑定入参 materials 的 {{节点名称.字段}}。',
      '- reply_type="referencing"：直接输出已绑定入参 value。',
      '- content_type（reply_type=content 时）：TEXT 纯文本 / HTML 富文本 / TOOL 工具结果 JSON，默认 TEXT。',
      '- 默认 is_result=true（输出给用户）。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前指定回复节点：直接输出文本（content）或上游变量（referencing）、回复内容格式（TEXT/HTML/TOOL），以及是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const referencing = args.reply_type === 'referencing'
          const value = argReference(context, 'value')
          if (referencing && !value) {
            return new ErrorResult('reply_type=referencing 需要父节点传入入参 value，请改用 content 或说明缺少该入参')
          }
          if (!referencing) {
            const error = validatePromptVariables(context.lf, context.nodeId, args.content, 'content') ?? (args.content ? null : 'content 不能为空')
            if (error) return new ErrorResult(error)
          }
          const nodeData = readNodeData<Record<string, unknown>>(node)
          const content_type =
            args.content_type === 'HTML' || args.content_type === 'TOOL' ? args.content_type : (nodeData.content_type ?? 'TEXT')
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              reply_type: referencing ? 'referencing' : 'content',
              content: referencing ? '' : String(args.content),
              fields: referencing && value ? [...value] : [],
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? true),
              ...(referencing ? { content_type: 'TEXT' } : { content_type }),
            },
          })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description: '不调用模型，直接输出固定文本或某个上游变量；用于兜底话术、直接返回知识库可直接回答的内容（directly_return）或拼装最终输出',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
