import type LogicFlow from '@logicflow/core'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { AgentErrorResult, ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule, NodeReference } from '@/workflow-canvas/ai-generate/type'
import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'

/** knowledge-write-node（知识库写入）的 AI 生成配置：只有入参 documents（带分段的文档列表），无其他可配置项 */

/**
 * 入参 documents 的结构，逐字段对应后端 KnowledgeWriteParamSerializer / ParagraphInstanceSerializer / TagInstanceSerializer。
 * x-single：items 只描述引用值的元素结构，这里只接一个引用。
 */
const PARAGRAPH_SCHEMA = {
  type: 'object',
  properties: {
    content: { type: 'string', description: '分段内容，最长 102400 字' },
    title: { type: 'string', description: '分段标题，最长 256 字' },
    problem_list: { type: 'array', items: { type: 'string' }, description: '关联问题' },
    chunks: { type: 'array', items: { type: 'string' }, description: '子分块；不传按内容自动切分' },
    is_active: { type: 'boolean', description: '是否启用' },
  },
  required: ['content'],
}

const TAG_SCHEMA = {
  type: 'object',
  properties: {
    key: { type: 'string', description: '标签名，1–64 字' },
    value: { type: 'string', description: '标签值，1–128 字' },
  },
  required: ['key', 'value'],
}

const DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string', description: '文档名，1–128 字' },
    paragraphs: { type: 'array', items: PARAGRAPH_SCHEMA, description: '分段列表；为空则写入空文档' },
    tags: { type: 'array', items: TAG_SCHEMA, description: '文档标签；知识库中不存在的标签会自动创建' },
    meta: { type: 'object', description: '文档元数据；写入时会合并工作流来源信息' },
    source_file_id: { type: 'string', description: '源文件 id（UUID），用于关联原文件' },
    doc_strategy: { type: 'object', description: '文档处理策略（split 分段 / visual 视觉 / index 索引），一般不传，缺省用默认策略' },
  },
  required: ['name'],
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    documents: {
      type: 'array',
      items: DOCUMENT_SCHEMA,
      'x-single': true,
      description:
        '要写入的文档列表：直接写入引用 [文档分段节点ID, "paragraph_list"]；需要标签 / 关联问题 / 元数据时引用加工过的 [代码节点ID, "result"]。' +
        '不要接文档内容提取 / Web 站点的 document_list 或本地文件的 file_list（没有 paragraphs，写入后文档为空）',
      'x-bind': 'document_list',
    },
  },
  required: ['documents'],
}

const config: JsonObjectSchema = { type: 'object', properties: {} }

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: false }

/** 只有文本、没有分段的上游：接到写入节点不会报错，但写入的文档为空，必须先经过文档分段 */
const UNSPLIT_SOURCES: Record<string, string> = {
  [WorkflowNodeType.DocumentExtractNode]: '文档内容提取',
  [WorkflowNodeType.DataSourceWebNode]: 'Web 站点',
  [WorkflowNodeType.DataSourceLocalNode]: '本地文件',
}

/** 引用的上游节点：循环体内可能引用父画布节点，当前画布找不到时视为无法判断 */
function findSourceNode(lf: LogicFlow, nodeId: string) {
  const graphModel = lf.graphModel as LogicFlow['graphModel'] & { get_parent_nodes?: () => Array<{ id: string; type: string; properties: Record<string, unknown> }> }
  return getNode(lf, nodeId) ?? graphModel.get_parent_nodes?.().find((node) => node.id === nodeId)
}

/** 校验写入来源格式：文档分段的 paragraph_list 直接通过；明确没有分段的来源拒绝；其余（代码加工结果、工具输出等）交由运行时 */
function checkSource(context: NodeAgentContext, [refNodeId, field]: NodeReference): string | null {
  const source = findSourceNode(context.lf, refNodeId)
  if (!source) return null
  const type = String(source.type)
  if (type === WorkflowNodeType.DocumentSplitNode) {
    return field === 'paragraph_list' ? null : `文档分段节点只有 paragraph_list 能写入知识库，当前引用的是 ${field}`
  }
  const unsplit = UNSPLIT_SOURCES[type] ?? (source.properties.kind === WorkflowKind.DataSource ? '数据源' : undefined)
  if (unsplit) {
    return `${unsplit}的 ${field} 没有分段，写入后文档为空：请在它和知识库写入之间加文档分段节点，再把 documents 绑定到 [文档分段节点ID, "paragraph_list"]（需要标签等字段时再经自定义代码加工）`
  }
  return null
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'knowledge-write-node（知识库写入）配置要点：',
      '- 写入内容来自入参 documents（已绑定：文档分段的 paragraph_list，或加工过的自定义代码 result）；无需其他配置，直接调用 update 完成校验。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前知识库写入节点：把入参 documents 绑定为写入内容，并校验来源是带分段的文档列表，其余字段无需配置。写入后自动校验，通过即配置完成；不通过返回 error。',
        parameters: config,
        apply: async () => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const reference = argReference(context, 'documents')
          if (!reference) return new ErrorResult('缺少入参 documents：请把 documents 绑定到文档分段的 [文档分段节点ID, "paragraph_list"]')
          const sourceError = checkSource(context, reference)
          // 绑定由搭建 agent 决定，本节点改不了：直接结束并把原因交回，避免子 agent 反复重试
          if (sourceError) return new AgentErrorResult(sourceError)
          writeNodeProperties(node, { node_data: { ...readNodeData<Record<string, unknown>>(node), document_list: [...reference] } })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description:
    '把带分段的文档列表写入当前知识库并完成向量化，是知识库工作流的末端节点。入参 documents 引用文档分段的 paragraph_list；' +
    '要给文档带上标签（tags）、关联问题、元数据时，先用自定义代码在 paragraph_list 上加工再写入。上游不能直接是文档内容提取或数据源',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
