import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** document-extract-node（文档内容提取）的 AI 生成配置：只有入参文件列表（documents），无其他可配置项；返回拼接文本与逐篇文档列表 */

/**
 * 入参 documents / 返回 document_list 的结构，逐字段对应后端 DocumentExtractNode 读写的数据。
 * x-single：items 只描述引用值的元素结构，这里只接一个引用。
 */
const FILE_SCHEMA = {
  type: 'object',
  properties: {
    file_id: { type: 'string', description: '文件 id，按它读取文件内容' },
    name: { type: 'string', description: '文件名，按扩展名选择解析方式' },
    meta: { type: 'object', description: '来源信息，原样带到输出的 meta' },
  },
  required: ['file_id', 'name'],
}

const DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string', description: '源文件 id' },
    name: { type: 'string', description: '文档名；ZIP 会展开为包内每个文件各一项' },
    content: { type: 'string', description: '该文档全文' },
    meta: { type: 'object', description: '输入文件的 meta，并补 source_file_id' },
  },
  required: ['id', 'name', 'content'],
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    documents: {
      type: 'array',
      items: FILE_SCHEMA,
      'x-single': true,
      description:
        '要提取内容的文件列表：应用工作流常来自开始节点用户上传的 document，知识库工作流来自本地文件数据源的 file_list；' +
        '不要接已含文本的 document_list（如 Web 站点数据源的输出，没有 file_id）',
      'x-bind': 'document_list',
    },
  },
  required: ['documents'],
}

const config: JsonObjectSchema = { type: 'object', properties: {} }

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    content: {
      type: 'string',
      description: '全部文件的文本拼成的一个字符串：每个文件为 "### 文件名\\n正文"，文件之间用分隔线隔开；适合放进提示词',
    },
    document_list: {
      type: 'array',
      items: DOCUMENT_SCHEMA,
      description: '逐篇的文档列表，可直接作为文档分段的入参',
    },
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
  description: '提取用户上传文档的文本内容，供下游 AI 对话基于文档回答（如总结、问答）；知识库工作流中接在本地文件数据源之后，document_list 供文档分段',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
