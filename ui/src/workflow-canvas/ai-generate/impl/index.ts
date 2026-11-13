import { WorkflowMode } from '@/workflow-canvas/types'
import { useApplicationAgent } from '@/workflow-canvas/ai-generate/impl/application'
import { useKnowledgeAgent } from '@/workflow-canvas/ai-generate/impl/knowledge'
import { useToolAgent } from '@/workflow-canvas/ai-generate/impl/tool'
import type { AgentBindings, RunnableAgent } from '@/workflow-canvas/ai-generate/type'

/** 主画布模式 → 父 agent 工厂；循环体随主画布归一到对应模式 */
const agentByMode: Partial<Record<WorkflowMode, (bindings: AgentBindings) => RunnableAgent>> = {
  [WorkflowMode.Application]: useApplicationAgent,
  [WorkflowMode.ApplicationLoop]: useApplicationAgent,
  [WorkflowMode.Knowledge]: useKnowledgeAgent,
  [WorkflowMode.KnowledgeLoop]: useKnowledgeAgent,
  [WorkflowMode.Tool]: useToolAgent,
  [WorkflowMode.ToolLoop]: useToolAgent,
}

/** 按画布模式装配父 agent；未接入的模式兜底到应用工作流 */
export const useAgent = (workflowMode: WorkflowMode, bindings: AgentBindings): RunnableAgent => {
  return (agentByMode[workflowMode] ?? useApplicationAgent)(bindings)
}
