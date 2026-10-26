import { cloneDeep } from 'lodash'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums/knowledge'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, getKnowledgeListTool, loadKnowledge, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { defaultSearchSetting } from './constant'

/** search-knowledge-node（知识库检索）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    question: { type: 'string', description: '检索问题，通常为用户问题或问题优化的 answer', 'x-bind': 'question_reference_address' },
    images: { type: 'array', description: '可选的检索图片，引用上传图片列表；需要支持图片向量化的模型', 'x-bind': 'image_list' },
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
      '- 检索图片由可选入参 images 绑定；有图片时使用 embedding 或 blend，不使用 keywords。',
      '- show_knowledge：是否把检索到的分段展示给用户，默认 false。',
      '- 检索参数：top_n（默认 3）、similarity（0-1，默认 0.6）、search_mode（embedding/keywords/blend）、max_paragraph_char_number（默认 5000）。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前知识库检索节点：检索范围、检索参数、是否展示结果等。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const nodeData = readNodeData<Record<string, unknown> & { knowledge_setting?: Record<string, unknown> }>(node)
          const referencing =
            args.search_scope_type === 'referencing' ||
            (args.search_scope_type === undefined && nodeData.search_scope_type === 'referencing')
          const scope = argReference(context, 'scope')
          const ids = !referencing && Array.isArray(args.knowledge_ids) ? args.knowledge_ids.map(String) : []
          const knowledgeList = await loadKnowledge()
          const selected = ids.map((id) => knowledgeList.find((knowledge) => knowledge.id === id))
          if (selected.some((knowledge) => !knowledge)) {
            return new ErrorResult(`知识库不存在：${ids.filter((_, index) => !selected[index]).join(', ')}`)
          }
          if (new Set(selected.map((knowledge) => knowledge!.embedding_model_id)).size > 1) {
            return new ErrorResult('所选知识库的向量模型不一致，只能选择向量模型相同的知识库')
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
          if (referencing && !scope) {
            return new ErrorResult(
              '已将检索范围设为“引用”，但缺少可引用的入参 scope：需要父 agent 把 scope 绑定到一个上游知识库 id 列表或文档 id 列表，否则该节点校验不通过（页面已显示为“引用”，请补充引用变量）',
            )
          }
          return finishWithValidate(context)
        },
      },
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
