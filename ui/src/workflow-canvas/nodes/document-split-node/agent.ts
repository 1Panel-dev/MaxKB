import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { splitPatternOptions } from './constant'

/** document-split-node（文档分段）的 AI 生成配置：入参文档列表，配置分段策略及其参数（均按自定义常量写入），返回带分段的文档列表 */

const SPLIT_STRATEGIES = ['auto', 'custom', 'qa']
const LENGTH_MIN = 50
const LENGTH_MAX = 100000

/**
 * 入参 documents / 返回 paragraph_list 的结构，逐字段对应后端 DocumentSplitNode 读写的数据。
 * x-single：items 只描述引用值的元素结构，这里只接一个引用。
 */
const INPUT_DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string', description: '文档名；.xlsx / .xls 会按 sheet 拆成多篇' },
    content: { type: 'string', description: '文档全文，按分段策略切分' },
    id: { type: 'string', description: '源文件 id，写到输出的 source_file_id' },
    meta: { type: 'object', description: '来源信息，原样带到输出的 meta' },
  },
  required: ['name', 'content'],
}

const PARAGRAPH_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string', description: '分段标题（qa 策略为问题）' },
    content: { type: 'string', description: '分段内容' },
    problem_list: { type: 'array', items: { type: 'string' }, description: '关联问题：按配置加入分段标题 / 文档名称' },
    chunks: { type: 'array', items: { type: 'string' }, description: '按 chunk_size 切出的子分块' },
    is_active: { type: 'boolean', description: '固定为 true' },
  },
  required: ['content'],
}

const OUTPUT_DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string', description: '文档名（Excel 为 sheet 名）' },
    paragraphs: { type: 'array', items: PARAGRAPH_SCHEMA, description: '分段列表' },
    meta: { type: 'object', description: '输入文档的 meta，并补 knowledge_id、source_file_id' },
    source_file_id: { type: 'string', description: '输入文档的 id，没有则为 null' },
  },
  required: ['name', 'paragraphs'],
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    documents: {
      type: 'array',
      items: INPUT_DOCUMENT_SCHEMA,
      'x-single': true,
      description: '要分段的文档列表：文档内容提取或 Web 站点数据源的 document_list；不要直接接本地文件的 file_list（没有 content）',
      'x-bind': 'document_list',
    },
  },
  required: ['documents'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    split_strategy: { type: 'string', enum: SPLIT_STRATEGIES, description: '分段策略：auto 智能分段（推荐，默认）/ custom 高级分段 / qa QA 问答对' },
    chunk_size: { type: 'integer', description: `子分块长度，${LENGTH_MIN}–${LENGTH_MAX}，默认 256` },
    patterns: {
      type: 'array',
      items: { type: 'string' },
      description: `分段标识，仅 custom 策略：按先后顺序递归分割，可选 ${splitPatternOptions.map((pattern) => pattern.label).join('、')}，也可传自定义正则`,
    },
    limit: { type: 'integer', description: `分段长度，仅 custom 策略，${LENGTH_MIN}–${LENGTH_MAX}，默认 4096` },
    with_filter: { type: 'boolean', description: '自动清洗，仅 custom 策略：去掉重复多余的符号、空格、空行、制表符' },
    paragraph_title_relate_problem: { type: 'boolean', description: '分段标题设置为分段的关联问题，qa 策略不适用，默认 false' },
    document_name_relate_problem: { type: 'boolean', description: '文档名称设置为分段的关联问题，默认 false' },
  },
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    paragraph_list: {
      type: 'array',
      items: OUTPUT_DOCUMENT_SCHEMA,
      description: '带分段的文档列表（不是扁平的分段数组），可直接作为知识库写入的入参',
    },
  },
  additionalProperties: false,
}

/** 长度类配置：未传返回 undefined，非法返回错误文本 */
function lengthOf(value: unknown, label: string): number | string | undefined {
  if (value === undefined || value === null) return undefined
  const length = Number(value)
  return Number.isInteger(length) && length >= LENGTH_MIN && length <= LENGTH_MAX ? length : `${label} 应为 ${LENGTH_MIN}–${LENGTH_MAX} 的整数`
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'document-split-node（文档分段）配置要点：',
      '- 文档来自入参 documents（已绑定），无需另选。',
      '- split_strategy：没有特别要求用 auto；要按指定符号 / 标题层级切分用 custom，并给 patterns（如按 Markdown 标题切分传 ["#", "##"]）与 limit；内容本身是问答对时用 qa。',
      '- 只传需要设置的字段，其余保持默认；写入的都是自定义常量。',
    ].join('\n'),
    tools: [
      createUpdateTool(
        context,
        config,
        (args) => {
          const node = getNode(context.lf, context.nodeId)!
          const reference = argReference(context, 'documents')
          if (!reference) return '缺少入参 documents：需要上游传入文档列表，请先把 documents 绑定到文档来源节点'
          if (args.split_strategy !== undefined && !SPLIT_STRATEGIES.includes(String(args.split_strategy))) {
            return `split_strategy 不合法：${args.split_strategy}，可选 ${SPLIT_STRATEGIES.join(' / ')}`
          }
          const chunkSize = lengthOf(args.chunk_size, 'chunk_size')
          if (typeof chunkSize === 'string') return chunkSize
          const limit = lengthOf(args.limit, 'limit')
          if (typeof limit === 'string') return limit
          const patterns = Array.isArray(args.patterns)
            ? args.patterns.map((pattern) => splitPatternOptions.find((option) => option.label === pattern)?.value ?? String(pattern)).filter(Boolean)
            : undefined
          const booleanFields = ['with_filter', 'paragraph_title_relate_problem', 'document_name_relate_problem'].filter(
            (field) => typeof args[field] === 'boolean',
          )
          writeNodeProperties(node, {
            node_data: {
              ...readNodeData<Record<string, unknown>>(node),
              document_list: [...reference],
              ...(args.split_strategy !== undefined ? { split_strategy: String(args.split_strategy) } : {}),
              ...(chunkSize ? { chunk_size: chunkSize, chunk_size_type: 'custom' } : {}),
              ...(limit ? { limit, limit_type: 'custom' } : {}),
              ...(patterns ? { patterns, patterns_type: 'custom' } : {}),
              ...Object.fromEntries(booleanFields.flatMap((field) => [[field, args[field]], [`${field}_type`, 'custom']])),
            },
          })
          return null
        },
        '配置当前文档分段节点：分段策略及其参数，只传要设置的字段。写入后自动校验，通过即配置完成并交付输出字段 paragraph_list。',
      ),
    ],
  })
}

export default {
  description: '按分段策略把文档内容拆成分段列表，供知识库写入；上游接文档内容提取（本地文件）或 Web 站点数据源',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
