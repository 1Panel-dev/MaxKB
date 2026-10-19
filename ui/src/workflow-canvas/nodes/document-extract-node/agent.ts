import { createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** document-extract-node（文档内容提取）的 AI 生成配置：只有入参，无需额外配置 */

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
    prompt: ['document-extract-node（文档内容提取）配置要点：', '- 文档已由入参 documents 绑定，无需其他配置，直接调用 update 完成校验。'].join('\n'),
    tools: [createUpdateTool(context, config, () => null)],
  })
}

export default {
  description: '提取用户上传文档的文本内容，供下游 AI 对话基于文档回答（如总结、问答）',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
