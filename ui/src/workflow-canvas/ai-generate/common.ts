import type { ChatCompletionPayload } from '@/api/types'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { AgentBindings, AgentConfig, AgentMessage, AgentTool, Call, RunnableAgent, SseEvent, StreamItem, ToolCall } from './type'

/**
 * 跨模块共用的基础设施：agent 装配（useAgentConfig）、工具 schema、SSE 流式补全、
 * 委派时的历史裁剪（inheritMessages）与调试日志。
 */

const DEFAULT_MAX_ITERATIONS = 60

/**
 * 装配可运行 agent：统一负责唯一一条 system（本 agent prompt + 整体目标背景，继承来的父 system 并入其前），
 * 非 system 历史原样接在后面；结果回写 bindings.messages，供本 agent 的委派工具裁剪给下一级。
 */
export function useAgentConfig(config: AgentConfig, bindings: AgentBindings): RunnableAgent {
  const ownPrompt = bindings.context
    ? `${config.prompt}\n\n【本次生成的整体目标（背景，供理解链路；你仍只做自己那份）】\n${bindings.context}`
    : config.prompt
  const inherited = bindings.messages ?? []
  const inheritedSystem = inherited
    .filter((message) => message.role === 'system')
    .map((message) => message.content)
    .filter(Boolean)
    .join('\n\n')
  const prompt = inheritedSystem ? `${inheritedSystem}\n\n──────\n\n${ownPrompt}` : ownPrompt
  const messages: AgentMessage[] = [{ role: 'system', content: prompt }, ...inherited.filter((message) => message.role !== 'system')]
  bindings.messages = messages
  return {
    prompt,
    messages,
    tools: config.tools,
    modelId: bindings.modelId,
    resourceScope: bindings.resourceScope,
    call: bindings.call,
    position: bindings.position ?? [],
    maxIterations: bindings.maxIterations ?? DEFAULT_MAX_ITERATIONS,
  }
}

/**
 * 从父 agent 历史裁出子 agent 的初始历史：去掉在途这一轮尚未回填的 tool 结果，
 * 并把触发委派的 assistant 消息只留正文，避免悬空的 tool_calls 让下一轮请求被拒。
 */
export function inheritMessages(bindings: AgentBindings): AgentMessage[] {
  const source = bindings.messages ?? []
  let end = source.length
  while (end > 0 && source[end - 1]?.role === 'tool') end--
  const trimmed = source.slice(0, end)
  const last = trimmed.at(-1)
  if (last?.role === 'assistant' && last.tool_calls) {
    if (last.content) trimmed[trimmed.length - 1] = { role: 'assistant', content: last.content }
    else trimmed.pop()
  }
  return trimmed
}

export function toToolSchemas(tools: AgentTool[]): NonNullable<ChatCompletionPayload['tools']> {
  return tools.map((tool) => ({
    type: 'function',
    function: { name: tool.name, description: tool.description, parameters: tool.parameters },
  }))
}

// ============================================================
// SSE 流式补全
// ============================================================

/** 增量解析 SSE 文本块，返回完整事件与剩余未完整的 buffer。 */
export function parseSseChunk(buffer: string): { events: Array<SseEvent | 'DONE'>; rest: string } {
  const events: Array<SseEvent | 'DONE'> = []
  const parts = buffer.split('\n\n')
  const rest = parts.pop() ?? ''
  for (const part of parts) {
    for (const line of part.split('\n')) {
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6).trim()
      if (data === '[DONE]') {
        events.push('DONE')
        continue
      }
      try {
        events.push(JSON.parse(data) as SseEvent)
      } catch {
        // 忽略无法解析的行
      }
    }
  }
  return { events, rest }
}

/**
 * 经工作流 Store 按资源范围调用流式补全接口，逐条把条目交给 call.onNext；正常结束 onComplete()，
 * error 事件、非 SSE 响应、网络错误或缺少 completion 一律 onComplete(error)。
 */
export async function chatCompletion(
  resourceScope: string,
  modelId: string,
  payload: ChatCompletionPayload,
  call: Call<StreamItem>,
  signal: AbortSignal,
): Promise<void> {
  try {
    const response = await useWorkflowStore(resourceScope).postChatCompletion(modelId, payload, signal)
    const contentType = response.headers.get('Content-Type') ?? ''
    if (!contentType.includes('text/event-stream')) {
      const result = (await response.json().catch(() => null)) as { message?: string } | null
      throw new Error(result?.message ?? `HTTP ${response.status}`)
    }
    if (!response.body) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let completed = false
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const { events, rest } = parseSseChunk(buffer)
      buffer = rest
      for (const event of events) {
        if (event === 'DONE') continue
        if (event.type === 'delta') call.onNext({ type: 'delta', content: String(event.content ?? '') })
        else if (event.type === 'reasoning') call.onNext({ type: 'reasoning', content: String(event.content ?? '') })
        else if (event.type === 'tool_call') {
          call.onNext({ type: 'tool_call', id: String(event.id), name: String(event.name ?? ''), arguments: String(event.arguments ?? '') })
        } else if (event.type === 'completion') {
          completed = true
          call.onNext({
            type: 'completion',
            result: {
              content: String(event.content ?? ''),
              toolCalls: (event.toolCalls as ToolCall[] | undefined) ?? [],
              finishReason: (event.finishReason as string | undefined) ?? null,
              usage: (event.usage as Record<string, unknown> | undefined) ?? null,
              reasoningKey: (event.reasoningKey as string | undefined) ?? null,
              reasoningContent: (event.reasoningContent as string | undefined) ?? null,
            },
          })
        } else if (event.type === 'error') {
          throw new Error(String(event.message ?? '模型调用失败'))
        }
      }
    }
    if (!completed) throw new Error('流式响应缺少完整结果')
    call.onComplete?.()
  } catch (error) {
    call.onComplete?.(error instanceof Error ? error : new Error(String(error)))
  }
}

// ============================================================
// 调试日志
// ============================================================

/**
 * 生成过程调试日志（写 localStorage，每条带 position 层级路径），仅供排查；异常一律吞掉。
 * 浏览器控制台复制：copy(localStorage.getItem('workflow-ai-generate-debug-log'))
 */
const DEBUG_KEY = 'workflow-ai-generate-debug-log'
const DEBUG_MAX_ENTRIES = 3000
const DEBUG_MAX_CHARS = 3_000_000

export function clipForLog(value: unknown, limit = 6000): unknown {
  if (value === undefined) return undefined
  let text: string
  try {
    text = typeof value === 'string' ? value : JSON.stringify(value)
  } catch {
    text = String(value)
  }
  return text.length <= limit ? value : `${text.slice(0, limit)}…(+${text.length - limit}字)`
}

export function logDebug(entry: Record<string, unknown>): void {
  try {
    const raw = localStorage.getItem(DEBUG_KEY)
    const entries: unknown[] = raw ? JSON.parse(raw) : []
    entries.push({ ts: new Date().toISOString().slice(11, 23), ...entry })
    while (entries.length > DEBUG_MAX_ENTRIES) entries.shift()
    let serialized = JSON.stringify(entries)
    while (serialized.length > DEBUG_MAX_CHARS && entries.length > 1) {
      entries.shift()
      serialized = JSON.stringify(entries)
    }
    localStorage.setItem(DEBUG_KEY, serialized)
  } catch {
    // localStorage 不可用或超限时忽略
  }
}

export function clearDebugLog(): void {
  try {
    localStorage.removeItem(DEBUG_KEY)
  } catch {
    // ignore
  }
}
