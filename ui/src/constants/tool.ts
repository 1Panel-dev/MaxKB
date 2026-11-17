/** 工具筛选项共用的协议值和翻译 key，由使用方按当前语言展示。 */
import type { ToolType } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'

export const TOOL_TYPE_OPTIONS = [
  { labelKey: 'common.labels.all', value: '' },
  { labelKey: 'tool.types.custom', value: TOOL_TYPE.CUSTOM },
  { labelKey: 'tool.types.skill', value: TOOL_TYPE.SKILL },
  { labelKey: 'tool.types.workflow', value: TOOL_TYPE.WORKFLOW },
  { labelKey: 'tool.types.mcp', value: TOOL_TYPE.MCP },
  { labelKey: 'tool.types.dataSource', value: TOOL_TYPE.DATA_SOURCE },
] satisfies { labelKey: string; value: ToolType | '' }[]
