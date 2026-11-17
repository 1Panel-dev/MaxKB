/** 工具筛选项共用的协议值和翻译 key，由使用方按当前语言展示。 */
import type { ToolType } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'

export const TOOL_TYPE_OPTIONS = [
  { labelKey: 'common.labels.all', value: '' },
  { labelKey: 'tool.title', value: TOOL_TYPE.CUSTOM },
  { labelKey: 'tool.skill.label', value: TOOL_TYPE.SKILL },
  { labelKey: 'tool.workflow.label', value: TOOL_TYPE.WORKFLOW },
  { labelKey: 'tool.mcp.label', value: TOOL_TYPE.MCP },
  { labelKey: 'tool.dataSource.label', value: TOOL_TYPE.DATA_SOURCE },
] satisfies { labelKey: string; value: ToolType | '' }[]
