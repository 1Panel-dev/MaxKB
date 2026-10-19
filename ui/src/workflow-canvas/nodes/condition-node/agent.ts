import { randomId } from '@/utils/common'
import { getNode, readNodeData, refreshBranchAnchors, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { CONDITION_SCHEMA, createValidateTool, normalizeConditions, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { AgentTool, JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/**
 * condition-node（判断器）的 AI 生成配置。
 * 分支结构固定为 1 个 IF（首）+ 0..N 个 ELSE IF + 1 个 ELSE（尾），每个分支一个出口锚点 `${nodeId}_${branchId}_right`。
 * 分支按 id 逐个增、改、删，不整体替换，保证已连的出口不漂移；删除分支时同步清理其出口的下游连线。
 */

interface Branch {
  id: string
  type: string
  condition: 'and' | 'or'
  conditions: unknown[]
}

const BRANCH_PARAMETERS = {
  condition: { type: 'string', enum: ['and', 'or'], description: '本分支多条件之间：and 全部满足 / or 任一满足，默认 and' },
  conditions: { type: 'array', items: CONDITION_SCHEMA, description: '本分支的条件，至少一条' },
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    fields: { type: 'array', items: {}, description: '分支条件里被比较的上游变量，可多个' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    branches: {
      type: 'array',
      items: { type: 'object', properties: BRANCH_PARAMETERS },
      description: 'IF / ELSE IF 分支及其条件，ELSE 固定兜底；经分支工具逐个配置',
    },
  },
  required: ['branches'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    branch_name: { type: 'string', description: '命中的分支名称' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  const node = () => getNode(context.lf, context.nodeId)!

  const readBranches = (): Branch[] => {
    const branches = readNodeData<{ branch?: Branch[] }>(node()).branch
    if (Array.isArray(branches) && branches.length) return branches
    return [
      { id: randomId(), type: 'IF', condition: 'and', conditions: [] },
      { id: randomId(), type: 'ELSE', condition: 'and', conditions: [] },
    ]
  }

  /** 写回分支：ELSE 固定在末尾，条件分支按顺序重排类型，并刷新出口锚点 */
  const writeBranches = (branches: Branch[]) => {
    const conditionBranches = branches.filter((branch) => branch.type !== 'ELSE')
    const elseBranch = branches.find((branch) => branch.type === 'ELSE') ?? { id: randomId(), type: 'ELSE', condition: 'and', conditions: [] }
    conditionBranches.forEach((branch, index) => (branch.type = index === 0 ? 'IF' : `ELSE IF ${index}`))
    writeNodeProperties(node(), { node_data: { ...readNodeData<Record<string, unknown>>(node()), branch: [...conditionBranches, elseBranch] } })
    refreshBranchAnchors(node())
  }

  const describe = (branch: Branch) => ({
    branch_id: branch.id,
    type: branch.type,
    source_anchor_id: `${context.nodeId}_${branch.id}_right`,
    condition: branch.condition,
    conditions: branch.conditions,
  })

  const tools: AgentTool[] = [
    {
      name: 'get_branches',
      description: '查看本节点当前全部分支（含默认的 IF 与 ELSE）及其 branch_id、出口 source_anchor_id、条件。增改删前先调用它。',
      parameters: { type: 'object', properties: {} },
      apply: () => ({ branches: readBranches().map(describe) }),
    },
    {
      name: 'update_branch',
      description: '原地修改 IF 或某个 ELSE IF 分支的条件，branch_id 与出口不变、已连的边不受影响。默认 IF 分支要先用它配好条件。',
      parameters: { type: 'object', properties: { branch_id: { type: 'string' }, ...BRANCH_PARAMETERS }, required: ['branch_id', 'conditions'] },
      apply: (args) => {
        const branches = readBranches()
        const branch = branches.find((item) => item.id === args.branch_id)
        if (!branch) return { error: `分支不存在: ${args.branch_id}` }
        if (branch.type === 'ELSE') return { error: 'ELSE 分支没有条件' }
        const conditions = normalizeConditions(context, args.conditions, 'conditions')
        if (typeof conditions === 'string') return { error: conditions }
        if (!conditions.length) return { error: '条件分支至少一条条件' }
        branch.conditions = conditions
        if (args.condition) branch.condition = args.condition === 'or' ? 'or' : 'and'
        writeBranches(branches)
        return describe(branch)
      },
    },
    {
      name: 'add_branch',
      description: '新增一个 ELSE IF 分支（自动插在 ELSE 前），返回其 branch_id 与出口 source_anchor_id，供建图 agent 连线。',
      parameters: { type: 'object', properties: BRANCH_PARAMETERS, required: ['conditions'] },
      apply: (args) => {
        const conditions = normalizeConditions(context, args.conditions, 'conditions')
        if (typeof conditions === 'string') return { error: conditions }
        if (!conditions.length) return { error: '条件分支至少一条条件' }
        const branches = readBranches()
        const branch: Branch = { id: randomId(), type: 'ELSE IF', condition: args.condition === 'or' ? 'or' : 'and', conditions }
        branches.splice(Math.max(branches.length - 1, 0), 0, branch)
        writeBranches(branches)
        return describe(branch)
      },
    },
    {
      name: 'delete_branch',
      description: '删除一个 ELSE IF 分支，并清理其出口已连的下游连线。IF 与 ELSE 固定保留。',
      parameters: { type: 'object', properties: { branch_id: { type: 'string' } }, required: ['branch_id'] },
      apply: (args) => {
        const branches = readBranches()
        const index = branches.findIndex((item) => item.id === args.branch_id)
        if (index < 0) return { error: `分支不存在: ${args.branch_id}` }
        if (index === 0 || branches[index]!.type === 'ELSE') return { error: '只能删除 ELSE IF 分支（IF 与 ELSE 固定保留）' }
        const anchorId = `${context.nodeId}_${args.branch_id}_right`
        const edges = context.lf.graphModel.edges.filter((edge) => edge.sourceAnchorId === anchorId)
        edges.forEach((edge) => context.lf.deleteEdge(edge.id))
        branches.splice(index, 1)
        writeBranches(branches)
        return { deleted: args.branch_id, removedEdges: edges.length }
      },
    },
    createValidateTool(context),
  ]

  return useNodeAgent(context, {
    prompt: [
      'condition-node（判断器）配置要点：',
      '- 固定结构：IF（第一个）+ 0..N 个 ELSE IF + ELSE（最后）。IF 与 ELSE 固定存在；ELSE IF 用 add_branch 增、delete_branch 删。',
      '- 先 get_branches 看现有分支（默认 1 个 IF + 1 个 ELSE）；先想清楚要分几路、每路判什么。',
      '- 第一路条件用 update_branch 配到默认 IF 上，其余每一路各 add_branch 一条 ELSE IF；ELSE 留作兜底。',
      '- 条件 field 使用已绑定入参 fields 中的引用；compare 取枚举值；为空/不为空/为真/不为真无需 value。',
      '- 全部配好后调 validate 收尾。结论里逐条列出各分支的 branch_id、source_anchor_id 与条件含义，供建图 agent 连线。',
    ].join('\n'),
    tools,
  })
}

export default {
  description:
    '相当于 if / else if / else：按条件把流程分到不同出口（IF、ELSE IF n、ELSE 各一个出口）；先 configure_node 配好分支，再 get_node_anchors 取各分支出口接下游。' +
    '常见：知识库检索后 is_hit_handling_method_list 非空 → 指定回复引用 directly_return，paragraph_list 非空 → AI 对话，否则 → 兜底回复',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
