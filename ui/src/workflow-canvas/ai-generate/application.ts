import { getMenuNodes } from '@/workflow-canvas/node-menu/menu'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { loopModeOf } from './tools/canvas'
import { inheritMessages, useAgentConfig } from './common'
import { createAgent } from './create-agent'
import { AgentSuccessResult, ErrorResult } from './tools/result'
import { renderNodeFunction } from './tools/node'
import {
  addEdgeTool,
  addNodeTool,
  configureNodeTool,
  deleteEdgeTool,
  deleteNodeTool,
  getCanvasDetailTool,
  getNodeAnchorsTool,
  layoutTool,
  nodeAgentFor,
  getToolsTool,
  validateTool,
} from './tools'
import type { AgentBindings, AgentTool, RunnableAgent } from './type'

/**
 * 应用工作流（Application）的父 agent：把每个节点当作一个函数（说明、形参、返回字段），
 * 先委派规划器据需求组合出蓝图，再亲手建图（含循环体，经 lf_id 跨画布），字段配置委派给各节点配置 agent，最后校验。
 */

function nodeLine(type: string, label: string): string {
  return renderNodeFunction(type, label, nodeAgentFor(type)!)
}

/** 可用节点函数：只列已接入 AI 生成的节点，循环体专属节点单列 */
function renderCatalog(bindings: AgentBindings): string {
  const supported = (nodes: Array<{ type: string; label: string }>) => nodes.filter((node) => nodeAgentFor(node.type))
  const mainGroups = getMenuNodes(bindings.workflowMode).map((group) => ({ label: group.label, nodes: supported(group.list) }))
  const mainTypes = new Set(mainGroups.flatMap((group) => group.nodes.map((node) => node.type)))
  const loopOnly = supported(getMenuNodes(loopModeOf(bindings.workflowMode)).flatMap((group) => group.list)).filter(
    (node) => !mainTypes.has(node.type),
  )
  const sections = mainGroups
    .filter((group) => group.nodes.length)
    .map((group) => `【${group.label}】\n${group.nodes.map((node) => nodeLine(node.type, node.label)).join('\n\n')}`)
  sections.push(`【工具】\n${nodeLine(WorkflowNodeType.ToolLib, '工具')}`)
  if (loopOnly.length)
    sections.push(`【仅循环体内可用（lf_id=所在循环节点 id）】\n${loopOnly.map((node) => nodeLine(node.type, node.label)).join('\n\n')}`)
  return sections.join('\n\n')
}

const GUIDE = `你是 MaxKB「智能体工作流」的搭建助手，在 LogicFlow 画布上按用户需求用建图工具亲手把流程搭出来（含循环体）。下方「可用节点」把每个节点写成一个函数：注释为说明（做什么、何时用、与上下游怎么配合）与可配置项，形参为它需要上游提供的数据，返回值为可被 [节点ID, 字段] 引用的输出字段（[字段名] 为按配置生成的动态字段）。搭画布就是把这些函数组合成一段程序：判断器 / 意图识别是分支，循环节点是 for，前一个节点的返回值是后一个节点的实参。

约定：
- 画布固定节点：base-node（基本信息）与 start-node（开始，id 固定 "start-node"），不可新增/删除/配置。start-node 输出 question（用户问题）；全局变量用 ["global", 字段] 引用。
- 引用格式：[节点ID, 字段]；提示词里的变量写 {{节点名称.字段}}（如 {{开始.question}}）。节点名称以 add_node 返回的 name 为准。
- 画布用 lf_id 标识：主画布 "main"（或省略）；循环体 = 该循环节点 id。每个循环体固定有 loop-start-node（输出 index、item）。

【从零搭建】
1. 先调 plan：规划器据需求组合节点函数，产出蓝图 { blueprint, notes }。之后照蓝图建。
2. 用 add_node(type, source_anchor_id) 建节点并接上游：第一个节点接 "start-node"；普通链式连接传上游节点 id；判断器 / 意图识别要先 configure_node 配好分支（requirement 写清分几路、各路条件或分类），再 get_node_anchors 取各分支出口接下游；多分支汇合用 add_edge 补入边。
3. 循环：主画布 add_node 建 loop-node 并 configure_node 配循环方式；再带 lf_id=该循环节点 id 往循环体建（首节点 source_anchor_id="loop-start-node"），循环体内节点用 lf_id=该循环 id 配置；无限循环必须放 loop-break-node。
4. 节点建好接好后 configure_node(nodeId, args, requirement, returns?) 配置，相当于调用这个函数：
   - args 传实参：形参名 → 上游引用 [节点ID, 字段]（多引用形参传列表），按蓝图的数据流给，框架会校验并绑定；
   - requirement 写配置要求（提示词只写要求、模型 / 知识库只写意图），节点配置 agent 会生成内容并查出真实资源；
   - 节点有 [字段名] 动态返回时，returns 列出要求产出的字段名（如参数提取的 city、date），下游按这些字段引用。
   同一轮可并发配置多个节点；但实参要引用上游的动态返回字段时，先配上游，按其交付的 outputs 再配下游。
5. 流程末端必须是能作为结束的节点（AI 对话、指定回复、表单等），面向用户的最终回答 is_result=true，中间加工步骤 is_result=false。
6. 全部完成后调 validate，problems 非空就按提示修复，直到 qualified=true，再调 layout 整理布局。

【续聊修改】先 get_canvas_detail 看现状，再用 add_node / add_edge / delete_node / delete_edge / configure_node 就地修改（循环体内传对应 lf_id），改完同样 validate。

完成后用一段话向用户总结搭了什么、还需要用户补充什么（如尚未创建知识库）即结束。`

function buildPrompt(bindings: AgentBindings): string {
  return `${GUIDE}\n\n======== 可用节点 ========\n${renderCatalog(bindings)}`
}

const PLAN_GUIDE = `你是 MaxKB「智能体工作流」的规划器。下方【可用节点】把每个节点写成一个函数（说明、形参、返回字段）。根据用户需求，像写程序一样组合这些函数，产出一份执行蓝图供搭建 agent 照着建。你只规划、不改画布。

思路：
- 先拆解需求：最终要给用户什么输出；为得到它需要哪些中间数据；每份数据由哪个节点函数的返回值提供。
- 按数据依赖排顺序：每个节点的形参都要有上游返回值（或开始节点的 question、全局变量）来提供，类型要对得上（如循环的 array 需要上游返回 array）。
- 需要按条件 / 分类走不同处理时用分支（condition-node / intent-node），需要逐项处理一组数据时用循环（loop-node）。
- 只放需求实际需要的节点；末端必须是能输出给用户的节点，最终回答 is_result=true、中间步骤 false。
- 需要外部工具时先 get_tools 看有哪些可用工具。需求含糊时按最常见理解规划，并在 notes 写明假设。

blueprint 元素 { type, intent, args?, returns?, children?, branches? }：
- intent：一句话写清它在链路里做什么与配置要求（AI 对话的角色 / 目标 / 输出、检索什么、判断条件、表单收集哪些字段）；
- args：每个形参由谁提供，写成 形参名 → "上游节点.返回字段"（如 question → "开始.question"、materials → ["知识库检索.data", "开始.question"]）；
- returns：有 [字段名] 动态返回的节点，列出要产出的字段名与类型（如参数提取 { city: string, date: string }）；
- loop-node 用 children 装循环体；condition-node / intent-node 用 branches（[{cond, children}]，最后一个为 else / 其他）。
想清楚后调 submit_plan 交出，交出即结束。`

const PLAN_TASK = '结合用户这次的需求，组合可用节点函数设计出蓝图，调用 submit_plan 交出。'

function submitPlanTool(): AgentTool {
  return {
    name: 'submit_plan',
    description: '交出规划：blueprint 节点树，notes 设计思路与关键假设。交出即结束。',
    parameters: {
      type: 'object',
      properties: {
        blueprint: { type: 'array', items: { type: 'object' } },
        notes: { type: 'string' },
      },
      required: ['blueprint'],
    },
    apply: (args) =>
      new AgentSuccessResult({
        blueprint: Array.isArray(args.blueprint) ? args.blueprint : [],
        notes: typeof args.notes === 'string' ? args.notes : '',
      }),
  }
}

/** 规划委派：起规划器子 agent（继承父对话），产出蓝图后上抛给父 agent */
function planTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'plan',
    description: '（从零搭建的第一步）委派规划器据需求组合节点函数并产出蓝图，返回 { blueprint, notes }。',
    parameters: { type: 'object', properties: {} },
    apply: () => {
      const plannerBindings: AgentBindings = {
        ...bindings,
        position: [...(bindings.position ?? []), 'plan'],
        messages: inheritMessages(bindings),
        maxIterations: 10,
      }
      const planner = createAgent(
        useAgentConfig(
          {
            prompt: `${PLAN_GUIDE}\n\n======== 可用节点 ========\n${renderCatalog(bindings)}`,
            tools: [getToolsTool(bindings), submitPlanTool()],
          },
          plannerBindings,
        ),
      )
      const promise = planner.run(PLAN_TASK).then((result) => {
        const plan = result.data as { blueprint?: unknown[] } | undefined
        if (result.status !== 'done' || !plan || typeof plan !== 'object' || !plan.blueprint?.length) {
          return new ErrorResult(typeof result.data === 'string' && result.data ? result.data : '规划未产出蓝图')
        }
        return plan
      })
      return { promise, cancel: planner.stop }
    },
  }
}

/** 应用工作流父 agent 的装配工厂 */
export function useApplicationAgent(bindings: AgentBindings): RunnableAgent {
  return useAgentConfig(
    {
      prompt: buildPrompt(bindings),
      tools: [
        planTool(bindings),
        getCanvasDetailTool(bindings),
        getNodeAnchorsTool(bindings),
        getToolsTool(bindings),
        addNodeTool(bindings),
        addEdgeTool(bindings),
        deleteNodeTool(bindings),
        deleteEdgeTool(bindings),
        configureNodeTool(bindings),
        validateTool(bindings),
        layoutTool(bindings),
      ],
    },
    bindings,
  )
}
