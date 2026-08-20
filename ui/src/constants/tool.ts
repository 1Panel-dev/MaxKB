import { TOOL_TYPE } from '@/api/enums'
import type { OptionItem, ToolType } from '@/api/types'
export const TOOL_TYPE_OPTIONS: OptionItem<ToolType | ''>[] = [
  { label: '全部', value: '' },
  { label: '工具', value: TOOL_TYPE.CUSTOM },
  { label: 'Skills', value: TOOL_TYPE.SKILL },
  { label: '工作流', value: TOOL_TYPE.WORKFLOW },
  { label: 'MCP', value: TOOL_TYPE.MCP },
  { label: '数据源', value: TOOL_TYPE.DATA_SOURCE },
]
