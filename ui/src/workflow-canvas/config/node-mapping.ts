import { TOOL_TYPE, type ToolType } from '@/api/types/workspace-tool'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import * as NodeData from './node-data'
interface WorkflowModelNode {
  properties?: {
    node_data?: {
      tool_type?: ToolType
    }
  }
  type: WorkflowNodeType
}
type WorkflowNodeMatcher = (node: unknown) => boolean
export const workflowModelDict: Record<WorkflowMode, WorkflowNodeMatcher> = {
  [WorkflowMode.Application]: (value) => {
    const node = value as WorkflowModelNode
    return (
      [
        WorkflowNodeType.Application,
        WorkflowNodeType.ToolWorkflowLib,
        WorkflowNodeType.ToolLib,
      ].includes(node.type) && node?.properties?.node_data?.tool_type !== TOOL_TYPE.DATA_SOURCE
    )
  },
  [WorkflowMode.ApplicationLoop]: (value) => {
    const node = value as WorkflowModelNode
    return (
      [
        WorkflowNodeType.Application,
        WorkflowNodeType.ToolWorkflowLib,
        WorkflowNodeType.ToolLib,
      ].includes(node.type) && node?.properties?.node_data?.tool_type !== TOOL_TYPE.DATA_SOURCE
    )
  },
  [WorkflowMode.Knowledge]: (value) => {
    const node = value as WorkflowModelNode
    return [WorkflowNodeType.ToolWorkflowLib, WorkflowNodeType.ToolLib].includes(node.type)
  },
  [WorkflowMode.KnowledgeLoop]: (value) => {
    const node = value as WorkflowModelNode
    return (
      [WorkflowNodeType.ToolWorkflowLib, WorkflowNodeType.ToolLib].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== TOOL_TYPE.DATA_SOURCE
    )
  },
  [WorkflowMode.Tool]: (value) => {
    const node = value as WorkflowModelNode
    return (
      [WorkflowNodeType.ToolWorkflowLib, WorkflowNodeType.ToolLib].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== TOOL_TYPE.DATA_SOURCE
    )
  },
  [WorkflowMode.ToolLoop]: (value) => {
    const node = value as WorkflowModelNode
    return (
      [WorkflowNodeType.ToolWorkflowLib, WorkflowNodeType.ToolLib].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== TOOL_TYPE.DATA_SOURCE
    )
  },
}
export const nodeDict: Partial<Record<WorkflowNodeType, Record<string,any>>> = {
  [WorkflowNodeType.AiChat]: NodeData.aiChatNode,
  [WorkflowNodeType.SearchKnowledge]: NodeData.searchKnowledgeNode,
  [WorkflowNodeType.SearchDocument]: NodeData.searchDocumentNode,
  [WorkflowNodeType.Question]: NodeData.questionNode,
  [WorkflowNodeType.Condition]: NodeData.conditionNode,
  [WorkflowNodeType.Base]: NodeData.baseNode,
  [WorkflowNodeType.Start]: NodeData.startNode,
  [WorkflowNodeType.Reply]: NodeData.replyNode,
  [WorkflowNodeType.ToolLib]: NodeData.toolNode,
  [WorkflowNodeType.ToolWorkflowLib]: NodeData.toolWorkflowLibNode,
  [WorkflowNodeType.ToolLibCustom]: NodeData.toolNode,
  [WorkflowNodeType.RerankerNode]: NodeData.rerankerNode,
  [WorkflowNodeType.FormNode]: NodeData.formNode,
  [WorkflowNodeType.Application]: NodeData.applicationNode,
  [WorkflowNodeType.DocumentExtractNode]: NodeData.documentExtractNode,
  [WorkflowNodeType.DocumentSplitNode]: NodeData.documentSplitNode,
  [WorkflowNodeType.ImageUnderstandNode]: NodeData.imageUnderstandNode,
  [WorkflowNodeType.TextToSpeechNode]: NodeData.textToSpeechNode,
  [WorkflowNodeType.SpeechToTextNode]: NodeData.speechToTextNode,
  [WorkflowNodeType.ImageGenerateNode]: NodeData.imageGenerateNode,
  [WorkflowNodeType.VariableAssignNode]: NodeData.variableAssignNode,
  [WorkflowNodeType.McpNode]: NodeData.mcpNode,
  [WorkflowNodeType.TextToVideoGenerateNode]: NodeData.textToVideoNode,
  [WorkflowNodeType.ImageToVideoGenerateNode]: NodeData.imageToVideoNode,
  [WorkflowNodeType.IntentNode]: NodeData.intentNode,
  [WorkflowNodeType.LoopNode]: NodeData.loopNode,
  [WorkflowNodeType.LoopBodyNode]: NodeData.loopBodyNode,
  [WorkflowNodeType.LoopStartNode]: NodeData.loopStartNode,
  [WorkflowNodeType.LoopBreakNode]: NodeData.loopBodyNode,
  [WorkflowNodeType.LoopContinueNode]: NodeData.loopContinueNode,
  [WorkflowNodeType.VariableSplittingNode]: NodeData.variableSplittingNode,
  [WorkflowNodeType.VideoUnderstandNode]: NodeData.videoUnderstandNode,
  [WorkflowNodeType.ParameterExtractionNode]: NodeData.parameterExtractionNode,
  [WorkflowNodeType.VariableAggregationNode]: NodeData.variableAggregationNode,
  [WorkflowNodeType.KnowledgeBase]: NodeData.knowledgeBaseNode,
  [WorkflowNodeType.DataSourceLocalNode]: NodeData.dataSourceLocalNode,
  [WorkflowNodeType.DataSourceWebNode]: NodeData.dataSourceWebNode,
  [WorkflowNodeType.KnowledgeWriteNode]: NodeData.knowledgeWriteNode,
  [WorkflowNodeType.ToolBaseNode]: NodeData.toolBaseNode,
  [WorkflowNodeType.ToolStartNode]: NodeData.toolStartNode,
}
export const BasicComponentsNode: Partial<
  Record<WorkflowNodeType, typeof NodeData.aiChatNode | typeof NodeData.replyNode>
> = {
  [WorkflowNodeType.AiChat]: NodeData.aiChatNode,
  [WorkflowNodeType.Reply]: NodeData.replyNode,
}

export const defaultNodes = [NodeData.baseNode, NodeData.startNode]
