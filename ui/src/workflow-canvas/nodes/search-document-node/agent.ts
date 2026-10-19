import { cloneDeep } from 'lodash'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, createUpdateTool, getKnowledgeListTool, loadKnowledge, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { AgentTool, JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { compareOptions } from './constant'

/** search-document-node（文档标签检索）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const COMPARES = compareOptions.map((option) => option.value)

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    question: { type: 'string', description: '检索问题（search_mode=auto 时必传），通常为用户问题', 'x-bind': 'question_reference' },
    scope: { type: 'array', description: '由上游决定检索范围时的知识库 / 文档 id 列表（search_scope_type=referencing 时必传）', 'x-bind': 'search_scope_reference' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    search_scope_type: { type: 'string', enum: ['custom', 'referencing'], description: '检索范围：custom 选定知识库（默认），referencing 由入参 scope 决定' },
    knowledge_ids: { type: 'array', items: { type: 'string' }, description: 'search_scope_type=custom 时的知识库 id 列表' },
    search_scope_source: { type: 'string', enum: ['knowledge', 'document'], description: 'search_scope_type=referencing 时入参 scope 是知识库 id 还是文档 id' },
    search_mode: { type: 'string', enum: ['auto', 'custom'], description: 'auto 按检索问题自动匹配文档标签（默认），custom 手动设置标签过滤条件（仅 custom 范围可用）' },
    condition_type: { type: 'string', enum: ['AND', 'OR'], description: '手动条件之间：AND 全部满足 / OR 任一满足' },
    conditions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          key: { type: 'string', description: '标签名（get_knowledge_tags 返回的 key）' },
          compare: { type: 'string', enum: COMPARES, description: compareOptions.map((option) => `${option.value}=${option.label}`).join('，') },
          value: { type: 'string', description: '标签值' },
        },
        required: ['key', 'compare', 'value'],
      },
      description: 'search_mode=custom 时的标签过滤条件',
    },
  },
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    knowledge_list: { type: 'array', description: '命中的知识库列表' },
    document_list: { type: 'array', description: '命中的文档列表' },
  },
  additionalProperties: false,
}

function knowledgeTagsTool(context: NodeAgentContext): AgentTool {
  return {
    name: 'get_knowledge_tags',
    description: '列出所选知识库的文档标签 [{key, values:[...]}]，手动设置标签条件前调用。',
    parameters: {
      type: 'object',
      properties: { knowledge_ids: { type: 'array', items: { type: 'string' } } },
      required: ['knowledge_ids'],
    },
    apply: async (args) => {
      const knowledgeIds = Array.isArray(args.knowledge_ids) ? args.knowledge_ids.map(String) : []
      const tags = await useWorkflowStore(context.bindings.resourceScope).getKnowledgeTags(knowledgeIds)
      return tags.slice(0, 100).map((tag) => ({ key: tag.key, values: tag.values.slice(0, 20).map((item) => item.value) }))
    },
  }
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'search-document-node（文档标签检索）配置要点：',
      '- 检索范围默认 search_scope_type="custom"，先 get_knowledge_list 选 knowledge_ids；已绑定入参 scope 时才用 "referencing"，并给 search_scope_source。',
      '- search_mode="auto" 按已绑定入参 question 自动匹配文档标签；需求明确给出标签过滤条件时用 "custom"，先 get_knowledge_tags 查标签，再写 conditions。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, async (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const nodeData = readNodeData<Record<string, unknown>>(node)
        const referencing = args.search_scope_type === 'referencing'
        const scope = argReference(context, 'scope')
        if (referencing && !scope) return 'search_scope_type=referencing 需要父节点传入入参 scope，请改用 custom 或说明缺少该入参'
        const searchMode = args.search_mode === 'custom' && !referencing ? 'custom' : 'auto'
        if (searchMode === 'auto' && !argReference(context, 'question')) return 'search_mode=auto 需要父节点传入入参 question，请改用 custom 或说明缺少该入参'
        const ids = !referencing && Array.isArray(args.knowledge_ids) ? args.knowledge_ids.map(String) : []
        const knowledgeList = await loadKnowledge()
        const selected = ids.map((id) => knowledgeList.find((knowledge) => knowledge.id === id))
        if (selected.some((knowledge) => !knowledge)) return `知识库不存在：${ids.filter((_, index) => !selected[index]).join(', ')}`
        const conditions = (Array.isArray(args.conditions) ? args.conditions : []) as Array<Record<string, string>>
        if (searchMode === 'custom') {
          if (!conditions.length) return 'search_mode=custom 至少一条 conditions'
          const invalid = conditions.find((condition) => !condition.key || !COMPARES.includes(condition.compare as never))
          if (invalid) return `条件不合法：${JSON.stringify(invalid)}`
        }
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            knowledge_id_list: ids,
            knowledge_list: cloneDeep(selected),
            search_scope_type: referencing ? 'referencing' : 'custom',
            search_scope_source: referencing && args.search_scope_source === 'document' ? 'document' : 'knowledge',
            search_scope_reference: referencing && scope ? [...scope] : [],
            search_mode: searchMode,
            search_condition_type: args.condition_type === 'OR' ? 'OR' : 'AND',
            search_condition_list:
              searchMode === 'custom' ? conditions.map((condition) => ({ key: condition.key, compare: condition.compare, value: String(condition.value ?? '') })) : [],
          },
        })
        return null
      }),
      getKnowledgeListTool,
      knowledgeTagsTool(context),
    ],
  })
}

export default {
  description: '按文档标签在知识库中筛选文档（自动按问题匹配标签，或手动设置标签条件），输出命中的知识库与文档，可作为下游检索的范围',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
