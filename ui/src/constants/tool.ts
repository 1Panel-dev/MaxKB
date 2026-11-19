/** 工具筛选项共用的协议值和响应式文案。 */
import { computed, reactive } from 'vue'
import type { ToolType } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import { t } from '@/locales'

export const TOOL_TYPE_OPTIONS = reactive([
  { label: computed(() => t('common.labels.all')), value: '' },
  { label: computed(() => t('tool.title')), value: TOOL_TYPE.CUSTOM },
  { label: computed(() => t('tool.skill.label')), value: TOOL_TYPE.SKILL },
  { label: computed(() => t('tool.workflow.label')), value: TOOL_TYPE.WORKFLOW },
  { label: computed(() => t('tool.mcp.label')), value: TOOL_TYPE.MCP },
  { label: computed(() => t('resource.dataSource.label')), value: TOOL_TYPE.DATA_SOURCE },
]) satisfies { label: string; value: ToolType | '' }[]
