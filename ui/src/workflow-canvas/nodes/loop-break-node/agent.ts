import { createLoopConditionAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

export default createLoopConditionAgent(WorkflowNodeType.LoopBreakNode, 'Break')
