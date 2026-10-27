export interface ToolCalls {
  type: string
  icon?: string
  title: string
  content: { input?: unknown; output?: unknown }
}
