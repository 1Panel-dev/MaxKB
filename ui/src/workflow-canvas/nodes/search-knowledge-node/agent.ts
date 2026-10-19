import { cloneDeep } from 'lodash'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums/knowledge'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, createUpdateTool, getKnowledgeListTool, loadKnowledge, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { defaultSearchSetting } from './constant'

/** search-knowledge-node（知识库检索）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    question: { type: 'string', description: '检索问题，通常为用户问题或问题优化的 answer', 'x-bind': 'question_reference_address' },
    scope: { type: 'array', description: '由上游决定检索范围时的知识库 / 文档 id 列表（search_scope_type=referencing 时必传）', 'x-bind': 'search_scope_reference' },
  },
  required: ['question'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    search_scope_type: { type: 'string', enum: ['custom', 'referencing'], description: '检索范围：custom 选定知识库（默认），referencing 由入参 scope 决定' },
    knowledge_ids: { type: 'array', items: { type: 'string' }, description: 'search_scope_type=custom 时的知识库 id 列表' },
    search_scope_source: { type: 'string', enum: ['knowledge', 'document'], description: 'search_scope_type=referencing 时入参 scope 是知识库 id 还是文档 id' },
    top_n: { type: 'number', description: '返回分段数，默认 3' },
    similarity: { type: 'number', description: '相似度阈值 0-1，默认 0.6' },
    search_mode: { type: 'string', enum: Object.values(KNOWLEDGE_SEARCH_MODE), description: '检索方式' },
    max_paragraph_char_number: { type: 'number', description: '引用分段最大字符数，默认 5000' },
    show_knowledge: { type: 'boolean', description: '是否把检索结果展示给用户，默认 false' },
  },
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    data: { type: 'string', description: '拼接好的分段文本，适合放进提示词' },
    paragraph_list: { type: 'array', description: '检索到的分段（title、content、similarity 等）；为空表示没检索到' },
    is_hit_handling_method_list: { type: 'array', description: '满足直接回答的分段；非空表示命中可直接返回的内容' },
    directly_return: { type: 'string', description: '满足直接回答的分段内容，可直接回复给用户' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'search-knowledge-node（知识库检索）配置要点：',
      '- 检索范围默认 search_scope_type="custom"，用 knowledge_ids 选定知识库；已绑定入参 scope 时才用 "referencing"，并给 search_scope_source。',
      '- knowledge_ids：先 get_knowledge_list 按需求挑选相关知识库（向量模型需一致）；工作空间没有合适知识库时传空数组并在结论里说明需用户补充。',
      '- 检索问题已由入参 question 绑定，无需配置。',
      '- show_knowledge：是否把检索到的分段展示给用户，默认 false。',
      '- 检索参数：top_n（默认 3）、similarity（0-1，默认 0.6）、search_mode（embedding/keywords/blend）、max_paragraph_char_number（默认 5000）。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, async (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const nodeData = readNodeData<Record<string, unknown> & { knowledge_setting?: Record<string, unknown> }>(node)
        const referencing = args.search_scope_type === 'referencing'
        const scope = argReference(context, 'scope')
        if (referencing && !scope) return 'search_scope_type=referencing 需要父节点传入入参 scope，请改用 custom 或说明缺少该入参'
        const ids = !referencing && Array.isArray(args.knowledge_ids) ? args.knowledge_ids.map(String) : []
        const knowledgeList = await loadKnowledge()
        const selected = ids.map((id) => knowledgeList.find((knowledge) => knowledge.id === id))
        if (selected.some((knowledge) => !knowledge)) return `知识库不存在：${ids.filter((_, index) => !selected[index]).join(', ')}`
        if (new Set(selected.map((knowledge) => knowledge!.embedding_model_id)).size > 1) {
          return '所选知识库的向量模型不一致，只能选择向量模型相同的知识库'
        }
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            knowledge_id_list: ids,
            knowledge_list: cloneDeep(selected),
            search_scope_type: referencing ? 'referencing' : 'custom',
            search_scope_source: referencing && args.search_scope_source === 'document' ? 'document' : 'knowledge',
            search_scope_reference: referencing && scope ? [...scope] : [],
            show_knowledge: typeof args.show_knowledge === 'boolean' ? args.show_knowledge : (nodeData.show_knowledge ?? false),
            knowledge_setting: {
              ...defaultSearchSetting,
              ...nodeData.knowledge_setting,
              ...(args.top_n !== undefined ? { top_n: Number(args.top_n) } : {}),
              ...(args.similarity !== undefined ? { similarity: Number(args.similarity) } : {}),
              ...(args.search_mode ? { search_mode: String(args.search_mode) } : {}),
              ...(args.max_paragraph_char_number !== undefined ? { max_paragraph_char_number: Number(args.max_paragraph_char_number) } : {}),
            },
          },
        })
        return null
      }),
      getKnowledgeListTool,
    ],
  })
}

export default {
  description:
    '在关联知识库中检索与问题相关的分段；用于基于知识库 / 文档回答，下游 AI 对话的提示词同时引用 data 与用户问题；' +
    '需要区分可直接回答 / 检索到 / 没检索到时，后接判断器分流',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
