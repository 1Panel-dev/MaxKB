import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** document-extract-node（文档内容提取）的 AI 生成配置：只有入参文档（documents），无其他可配置项 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    documents: { type: 'array', description: '要提取内容的文档，常来自开始节点用户上传的 document', 'x-bind': 'document_list' },
  },
  required: ['documents'],
}

const config: JsonObjectSchema = { type: 'object', properties: {} }

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    content: { type: 'string', description: '提取出的文档文本，适合放进提示词' },
    document_list: { type: 'array', description: '文档列表' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'document-extract-node（文档内容提取）配置要点：',
      '- 文档来自入参 documents（引用上游的文档列表），确认它能解析出要提取的文档；无需其他配置，直接调用 update 完成校验。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前文档内容提取节点：把入参 documents 绑定为待提取文档（document_list），其余字段无需配置。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段 content 与 document_list；不通过返回 error 继续修。',
        parameters: config,
        apply: async () => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const reference = argReference(context, 'documents')
          if (!reference) return new ErrorResult('缺少入参 documents：需要上游传入选中的文档列表，请先把 documents 绑定到文档来源节点')
          const nodeData = readNodeData<Record<string, unknown>>(node)
          writeNodeProperties(node, { node_data: { ...nodeData, document_list: [...reference] } })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description: '提取用户上传文档的文本内容，供下游 AI 对话基于文档回答（如总结、问答）',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
