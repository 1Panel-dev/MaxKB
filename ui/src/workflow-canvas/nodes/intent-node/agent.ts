import { omit } from 'lodash'
import { randomId } from '@/utils/common'
import { getNode, readNodeData, refreshBranchAnchors, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createValidateTool, getModelsTool, MODEL_FIELD_SCHEMA, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { AgentTool, JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/**
 * intent-node（意图识别）的 AI 生成配置。
 * 每个分类一个出口锚点 `${nodeId}_${branchId}_right`，"其他"分类固定在末尾。
 * 分类按 id 逐个增、改、删，保证已连的出口不漂移；删除分类时同步清理其出口的下游连线。
 */

interface IntentBranch {
  id: string
  content: string
  isOther: boolean
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    text: { type: 'string', description: '被分类的文本，通常为用户问题', 'x-bind': 'content_list' },
  },
  required: ['text'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    dialogue_number: { type: 'number', description: '历史对话轮数，默认 1' },
    dialogue_type: { type: 'string', enum: ['WORKFLOW', 'NODE'], description: '历史来源：WORKFLOW 工作流问答（默认），NODE 本节点问答' },
    branches: { type: 'array', items: { type: 'string' }, description: '分类列表，清晰互斥；"其他"固定兜底，经分类工具逐个配置' },
  },
  required: ['model', 'branches'],
}

/** update 只写模型与历史对话，分类由 add_branch / update_branch 管理 */
const updateSchema: JsonObjectSchema = { ...config, properties: omit(config.properties, 'branches'), required: ['model'] }

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    category: { type: 'string', description: '命中的分类' },
    reason: { type: 'string', description: '分类理由' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  const node = () => getNode(context.lf, context.nodeId)!

  const readBranches = (): IntentBranch[] => {
    const branches = readNodeData<{ branch?: IntentBranch[] }>(node()).branch
    if (Array.isArray(branches) && branches.length) return branches
    return [
      { id: randomId(), content: '', isOther: false },
      { id: randomId(), content: '其他', isOther: true },
    ]
  }

  /** 写回分类："其他"固定在末尾，并刷新出口锚点 */
  const writeBranches = (branches: IntentBranch[]) => {
    const other = branches.find((branch) => branch.isOther) ?? { id: randomId(), content: '其他', isOther: true }
    writeNodeProperties(node(), {
      node_data: { ...readNodeData<Record<string, unknown>>(node()), branch: [...branches.filter((branch) => !branch.isOther), other] },
    })
    refreshBranchAnchors(node())
  }

  const describe = (branch: IntentBranch) => ({
    branch_id: branch.id,
    content: branch.content,
    is_other: branch.isOther,
    source_anchor_id: `${context.nodeId}_${branch.id}_right`,
  })

  const tools: AgentTool[] = [
    {
      name: 'update',
      description: '写入模型与历史对话（轮数、来源）；被分类文本已由入参 text 绑定，分类用 add_branch / update_branch 管理。',
      parameters: updateSchema,
      apply: (args) => {
        const modelFields = resolveModelFields(context, args.model)
        if (typeof modelFields === 'string') return { error: modelFields }
        const nodeData = readNodeData<Record<string, unknown>>(node())
        writeNodeProperties(node(), {
          node_data: {
            ...nodeData,
            ...modelFields,
            dialogue_type: args.dialogue_type === 'NODE' || args.dialogue_type === 'WORKFLOW' ? args.dialogue_type : (nodeData.dialogue_type ?? 'WORKFLOW'),
            dialogue_number: Number(args.dialogue_number ?? nodeData.dialogue_number ?? 1),
          },
        })
        return { ok: true }
      },
    },
    {
      name: 'get_branches',
      description: '查看当前全部分类（含默认的空分类与"其他"）及其 branch_id、出口 source_anchor_id。',
      parameters: { type: 'object', properties: {} },
      apply: () => ({ branches: readBranches().map(describe) }),
    },
    {
      name: 'update_branch',
      description: '原地修改某个分类的描述，branch_id 与出口不变。默认的空分类要先用它填上第一个分类。"其他"不可修改。',
      parameters: { type: 'object', properties: { branch_id: { type: 'string' }, content: { type: 'string' } }, required: ['branch_id', 'content'] },
      apply: (args) => {
        const branches = readBranches()
        const branch = branches.find((item) => item.id === args.branch_id)
        if (!branch) return { error: `分类不存在: ${args.branch_id}` }
        if (branch.isOther) return { error: '"其他"分类不可修改' }
        if (!String(args.content ?? '').trim()) return { error: 'content 不能为空' }
        branch.content = String(args.content).trim()
        writeBranches(branches)
        return describe(branch)
      },
    },
    {
      name: 'add_branch',
      description: '新增一个分类（自动插在"其他"前），返回其 branch_id 与出口 source_anchor_id。',
      parameters: {
        type: 'object',
        properties: { content: { type: 'string', description: '分类描述，清晰且与其他分类互斥' } },
        required: ['content'],
      },
      apply: (args) => {
        if (!String(args.content ?? '').trim()) return { error: 'content 不能为空' }
        const branches = readBranches()
        const branch: IntentBranch = { id: randomId(), content: String(args.content).trim(), isOther: false }
        writeBranches([...branches.filter((item) => !item.isOther), branch, ...branches.filter((item) => item.isOther)])
        return describe(branch)
      },
    },
    {
      name: 'delete_branch',
      description: '删除一个分类，并清理其出口已连的下游连线。"其他"固定保留，且至少保留一个普通分类。',
      parameters: { type: 'object', properties: { branch_id: { type: 'string' } }, required: ['branch_id'] },
      apply: (args) => {
        const branches = readBranches()
        const branch = branches.find((item) => item.id === args.branch_id)
        if (!branch) return { error: `分类不存在: ${args.branch_id}` }
        if (branch.isOther) return { error: '"其他"分类固定保留' }
        if (branches.filter((item) => !item.isOther).length <= 1) return { error: '至少保留一个普通分类' }
        const anchorId = `${context.nodeId}_${branch.id}_right`
        const edges = context.lf.graphModel.edges.filter((edge) => edge.sourceAnchorId === anchorId)
        edges.forEach((edge) => context.lf.deleteEdge(edge.id))
        writeBranches(branches.filter((item) => item.id !== branch.id))
        return { deleted: branch.id, removedEdges: edges.length }
      },
    },
    getModelsTool(context),
    createValidateTool(context),
  ]

  return useNodeAgent(context, {
    prompt: [
      'intent-node（意图识别）配置要点：',
      '- 先 update 写入 model（已配置默认模型时传 "default"，否则 get_models 选 id）；被分类文本已由入参 text 绑定。',
      '- 再管理分类：get_branches 看现状；第一个分类用 update_branch 填到默认的空分类上，其余各 add_branch 一个；"其他"固定在末尾作兜底，无需新增。',
      '- 分类描述要清晰互斥（如 "售前咨询"、"售后问题"）。',
      '- 全部配好后调 validate 收尾。结论里逐条列出各分类的 branch_id 与 source_anchor_id，供建图 agent 连线。',
    ].join('\n'),
    tools,
  })
}

export default {
  description:
    '相当于 switch：用大模型把文本归入预设分类，每个分类一个出口，"其他"兜底；用于按问题类型走不同处理（售前 / 售后、闲聊 / 业务）。' +
    '先 configure_node 配好分类，再 get_node_anchors 取各分类出口接下游',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
