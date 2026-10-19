/** 函数参数在弹窗中的编辑形态 */
export interface LlmToolParameter {
  name: string
  type: string
  description: string
  required: boolean
}

/** OpenAI function calling 格式的函数定义 */
export interface LlmToolFunction {
  name: string
  description: string
  parameters: {
    type: 'object'
    properties: Record<string, { type: string; description: string }>
    required?: string[]
  }
}

export interface LlmTool {
  type: 'function'
  function: LlmToolFunction
}

export interface LlmToolsSetting {
  location: 'customize' | 'reference'
  reference: string[]
  tools: LlmTool[]
}

export const toolParameterTypes = ['string', 'number', 'integer', 'boolean', 'object', 'array']

/** 将任意 JSON 函数定义归一化为工具；缺少函数名时返回 null */
export function normalizeTool(value: unknown): LlmTool | null {
  const raw = value as { function?: Partial<LlmToolFunction> } & Partial<LlmToolFunction>
  const toolFunction = raw?.function ?? raw
  if (!toolFunction?.name) return null
  return {
    type: 'function',
    function: {
      name: toolFunction.name,
      description: toolFunction.description || '',
      parameters: toolFunction.parameters?.properties ? toolFunction.parameters : { type: 'object', properties: {} },
    },
  }
}
