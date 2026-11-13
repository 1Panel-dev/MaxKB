import { createValidateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** data-source-web-node（Web 站点数据源）的 AI 生成配置：流程入口，无入参也无配置项 */

const params: JsonObjectSchema = { type: 'object', properties: {} }

const config: JsonObjectSchema = { type: 'object', properties: {} }

/** 返回 document_list 的结构，逐字段对应后端 DataSourceWebNode 写入的数据 */
const DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string', description: '文档名：链接文字，没有则为页面地址' },
    content: { type: 'string', description: '页面正文，已转为 Markdown' },
    meta: { type: 'object', description: '含 source_type="web"、source_url 页面地址、selector 选择器及工作流来源信息' },
  },
  required: ['name', 'content', 'meta'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    document_list: {
      type: 'array',
      items: DOCUMENT_SCHEMA,
      description: '从根地址起逐层抓取到的页面列表，已含文本内容（没有 id / file_id），可直接作为文档分段的入参，不要再接文档内容提取',
    },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: 'data-source-web-node（Web 站点）没有配置项：根地址与选择器由用户在运行时填写，直接调用 validate 完成。',
    tools: [createValidateTool(context)],
  })
}

export default {
  description:
    '知识库工作流的入口数据源：运行时由用户输入根地址（可选选择器，默认 body），自动抓取 Web 页面（单链接对应单文档），输出含内容的文档列表；下游可直接接文档分段。新增时不接上游（省略 source_anchor_id），无配置项，无需 configure_node',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
