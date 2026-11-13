import { getMenuNodes } from '@/workflow-canvas/node-menu/menu'
import { WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import { loopModeOf } from '@/workflow-canvas/ai-generate/tools/canvas'
import { inheritMessages, useAgentConfig } from '@/workflow-canvas/ai-generate/common'
import { createAgent } from '@/workflow-canvas/ai-generate/create-agent'
import { renderNodeFunction, renderPlainNodeFunction, schemaType } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import { nodeAgentFor } from '@/workflow-canvas/ai-generate/tools'
import type { AgentBindings, AgentTool } from '@/workflow-canvas/ai-generate/type'

/**
 * 各画布模式父 agent 共享的机械装配：可用节点目录渲染、规划器委派、提示词拼装。
 * 各 impl/*\/index.ts 各自持有本模式的 GUIDE / 规划器提示词与工具集，仅复用这里的纯装配逻辑。
 */

type CatalogNode = ShapeItem & { type: string; label: string }

/** 节点 → 函数签名：已注册配置 agent 的按其声明渲染，其余按菜单文案与模板输出字段渲染 */
export function nodeLine(node: CatalogNode): string {
  const module = nodeAgentFor(node.type)
  if (module) return renderNodeFunction(node.type, node.label, module)
  const config = node.properties?.config as { fields?: Array<{ value: string; label: string }> } | undefined
  return renderPlainNodeFunction(node.type, node.label, node.text ?? '', config?.fields ?? [])
}

/**
 * 可用节点函数目录：与节点菜单（node-menu）一致，按画布模式列出全部菜单节点，循环体专属节点单列；
 * 末尾追加「工具」（tool-lib-node）函数，对应菜单的工具 / 数据源页签。
 */
export function renderCatalog(bindings: AgentBindings): string {
  const mainGroups = getMenuNodes(bindings.workflowMode)
  const mainTypes = new Set<string>(mainGroups.flatMap((group) => group.list.map((node) => node.type)))
  const loopOnly = getMenuNodes(loopModeOf(bindings.workflowMode))
    .flatMap((group) => group.list)
    .filter((node) => !mainTypes.has(node.type))
  const sections = mainGroups.filter((group) => group.list.length).map((group) => `【${group.label}】\n${group.list.map(nodeLine).join('\n\n')}`)
  const toolLib = nodeAgentFor(WorkflowNodeType.ToolLib)
  if (toolLib) sections.push(`【工具】\n${renderNodeFunction(WorkflowNodeType.ToolLib, '工具', toolLib)}`)
  if (loopOnly.length) sections.push(`【仅循环体内可用（lf_id=所在循环节点 id）】\n${loopOnly.map(nodeLine).join('\n\n')}`)
  return sections.join('\n\n')
}

/**
 * 知识库写入要求的文档列表结构，取自 knowledge-write-node 声明的形参 documents（唯一来源）。
 * 供目录里没有知识库写入节点的模式（如工具工作流）在产出要交给知识库工作流时引用。
 */
export function knowledgeDocumentsStructure(): string {
  return schemaType(nodeAgentFor(WorkflowNodeType.KnowledgeWriteNode)?.params.properties.documents)
}

export interface PlannerConfig {
  /** 规划器系统提示词（含本模式说明与可用节点） */
  guide: string
  /** 规划器任务指令 */
  task: string
  /** 规划器可用工具（如需查工具 / 数据源） */
  tools: AgentTool[]
}

/** 规划委派：起规划器子 agent（继承父对话），产出文字方案后上抛给父 agent */
export function createPlanTool(bindings: AgentBindings, planner: PlannerConfig): AgentTool {
  return {
    name: 'plan',
    description: '（从零搭建的第一步，或用户要求大改方案时）委派规划器据需求组合节点函数，写出文字方案，返回 { plan }。',
    parameters: { type: 'object', properties: {} },
    apply: () => {
      const plannerBindings: AgentBindings = {
        ...bindings,
        position: [...(bindings.position ?? []), 'plan'],
        messages: inheritMessages(bindings),
        maxIterations: 10,
      }
      const agent = createAgent(
        useAgentConfig({ prompt: planner.guide, tools: planner.tools }, plannerBindings),
      )
      const promise = agent.run(planner.task).then((result) => {
        const plan = typeof result.data === 'string' ? result.data.trim() : ''
        if (result.status !== 'done' || !plan) return new ErrorResult(plan || '规划未产出方案')
        return { plan }
      })
      return { promise, cancel: agent.stop }
    },
  }
}

/** 拼装父 agent 提示词：模式说明 + 可用节点目录 */
export function buildParentPrompt(guide: string, bindings: AgentBindings): string {
  return `${guide}\n\n======== 可用节点 ========\n${renderCatalog(bindings)}`
}
