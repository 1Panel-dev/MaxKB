/** 后端 Workspace 工具作用域枚举值。 */
export const TOOL_SCOPE = { INTERNAL: 'INTERNAL', SHARED: 'SHARED', WORKSPACE: 'WORKSPACE' } as const

/** 后端 Workspace 工具类型枚举值。 */
export const TOOL_TYPE = {
  CUSTOM: 'CUSTOM',
  DATA_SOURCE: 'DATA_SOURCE',
  INTERNAL: 'INTERNAL',
  MCP: 'MCP',
  SKILL: 'SKILL',
  WORKFLOW: 'WORKFLOW',
} as const

/** 工具执行记录的调用来源。 */
export const TOOL_RECORD_SOURCE = { APPLICATION: 'APPLICATION', KNOWLEDGE: 'KNOWLEDGE', TOOL: 'TOOL', TRIGGER: 'TRIGGER' } as const
