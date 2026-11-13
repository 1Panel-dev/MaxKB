import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** data-source-local-node（本地文件数据源）的 AI 生成配置：流程入口，无入参，只有上传限制 */

const params: JsonObjectSchema = { type: 'object', properties: {} }

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    file_type_list: {
      type: 'array',
      items: { type: 'string' },
      description: '允许上传的文件格式（大写扩展名），默认 TXT、DOCX、PDF、HTML、XLS、XLSX、ZIP、CSV、MD',
    },
    file_count_limit: { type: 'integer', description: '最多上传文件数，1–1000，默认 50' },
    file_size_limit: { type: 'integer', description: '单个文件大小上限（MB），1–1000，默认 100' },
  },
}

/** 返回 file_list 的结构，逐字段对应后端 DataSourceLocalNode 写入的数据（文件项原样展开后补 meta） */
const FILE_SCHEMA = {
  type: 'object',
  properties: {
    file_id: { type: 'string', description: '文件 id' },
    name: { type: 'string', description: '文件名，含扩展名' },
    meta: { type: 'object', description: '含 source_type="local"、source_file_id 及工作流来源信息' },
  },
  required: ['file_id', 'name', 'meta'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    file_list: {
      type: 'array',
      items: FILE_SCHEMA,
      description: '用户运行时上传的文件列表，只有文件信息、没有文本内容，需接文档内容提取解析',
    },
  },
  additionalProperties: false,
}

/** 上限类配置：未传返回 undefined，非法返回错误文本 */
function limitOf(value: unknown, label: string): number | string | undefined {
  if (value === undefined || value === null) return undefined
  const limit = Number(value)
  return Number.isInteger(limit) && limit >= 1 && limit <= 1000 ? limit : `${label} 应为 1–1000 的整数`
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'data-source-local-node（本地文件）配置要点：',
      '- 只有上传限制三项：文件格式、最多上传文件数、单个文件大小上限；没有特别要求时保持默认，直接调用 update（不传参数）完成校验。',
    ].join('\n'),
    tools: [
      createUpdateTool(
        context,
        config,
        (args) => {
          const node = getNode(context.lf, context.nodeId)!
          const fileCountLimit = limitOf(args.file_count_limit, 'file_count_limit')
          if (typeof fileCountLimit === 'string') return fileCountLimit
          const fileSizeLimit = limitOf(args.file_size_limit, 'file_size_limit')
          if (typeof fileSizeLimit === 'string') return fileSizeLimit
          const fileTypes = Array.isArray(args.file_type_list) ? args.file_type_list.map((fileType) => String(fileType).trim().toUpperCase()).filter(Boolean) : undefined
          if (fileTypes && !fileTypes.length) return 'file_type_list 至少包含一种文件格式'
          writeNodeProperties(node, {
            node_data: {
              ...readNodeData<Record<string, unknown>>(node),
              ...(fileTypes ? { file_type_list: fileTypes } : {}),
              ...(fileCountLimit ? { file_count_limit: fileCountLimit } : {}),
              ...(fileSizeLimit ? { file_size_limit: fileSizeLimit } : {}),
            },
          })
          return null
        },
        '配置当前本地文件数据源的上传限制，只传要修改的字段，其余保持不变。写入后自动校验，通过即配置完成并交付输出字段 file_list。',
      ),
    ],
  })
}

export default {
  description:
    '知识库工作流的入口数据源：运行时由用户上传本地文档，输出文件列表（不解析内容）；下游接文档内容提取。新增时不接上游（省略 source_anchor_id）',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
