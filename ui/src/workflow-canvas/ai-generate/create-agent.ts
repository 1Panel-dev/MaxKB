import { chatCompletion, clipForLog, logDebug, toToolSchemas } from './common'
import { AgentErrorResult, AgentSuccessResult, ErrorResult, isFailureResult, toToolResult, type ToolResult } from './tools/result'
import type {
  AgentHandle,
  AgentMessage,
  AgentPayload,
  AgentResult,
  AgentTool,
  Call,
  ChatCompletionResult,
  Executor,
  RunnableAgent,
  StreamItem,
  ToolCall,
} from './type'

/** 工具结果回喂模型的截断上限，避免上下文膨胀 */
const TOOL_RESULT_LIMIT = 8000
/** tool_end 事件里结果摘要的展示上限 */
const RESULT_SUMMARY_LIMIT = 200

function truncate(text: string, limit: number): string {
  return text.length > limit ? `${text.slice(0, limit)}…(truncated)` : text
}

function stringify(value: unknown): string {
  return typeof value === 'string' ? value : JSON.stringify(value ?? null)
}

function isExecutor(value: unknown): value is Executor {
  const candidate = value as Executor | null
  return !!candidate && typeof candidate === 'object' && typeof candidate.cancel === 'function' && candidate.promise instanceof Promise
}

function toExecutor(value: unknown): Executor {
  if (isExecutor(value)) return value
  return { promise: Promise.resolve(value), cancel: () => {} }
}

/**
 * 运行一台 agent：每轮流式补全 → 并发执行本轮工具 → 回填结果，直到模型不再调工具、
 * 某工具返回 AgentSuccessResult / AgentErrorResult 结束、被停止或超过轮次。工具返回 ErrorResult 或抛错时把错误回喂模型自愈。
 */
export function createAgent(agent: RunnableAgent): AgentHandle {
  const { tools, modelId, resourceScope, call, position, maxIterations } = agent
  const controller = new AbortController()
  const stopCallbacks: Array<() => void> = []
  const messages: AgentMessage[] = agent.messages

  const emit = (payload: AgentPayload) => call.onNext({ ...payload, position })

  const stop = () => {
    controller.abort()
    stopCallbacks.forEach((callback) => callback())
  }

  const finish = (result: AgentResult, error?: Error): AgentResult => {
    logDebug({ kind: 'end', pos: position, status: result.status, data: clipForLog(stringify(result.data ?? ''), 800) })
    if (result.status === 'error') emit({ type: 'error', message: stringify(result.data ?? '') })
    else if (result.status === 'done') emit({ type: 'done', data: result.data })
    call.onComplete?.(error)
    return result
  }

  async function run(requirement: string): Promise<AgentResult> {
    if (!modelId) return finish({ status: 'error', data: '缺少模型' })
    logDebug({ kind: 'run', pos: position, requirement: clipForLog(requirement, 800) })
    messages.push({ role: 'user', content: requirement })

    try {
      for (let iteration = 1; ; iteration++) {
        if (controller.signal.aborted) return finish({ status: 'stopped' })
        if (iteration > maxIterations) return finish({ status: 'error', data: `超过最大轮次 ${maxIterations}` })

        const response = await runTurn(resourceScope, modelId, messages, tools, emit, controller.signal)
        const toolCalls = response.toolCalls ?? []
        const assistantMessage: AgentMessage = { role: 'assistant', content: response.content || '' }
        // thinking 模型要求思考内容按原字段名回传，否则下一轮请求会被拒绝
        if (response.reasoningKey && response.reasoningContent) assistantMessage[response.reasoningKey] = response.reasoningContent
        if (toolCalls.length) assistantMessage.tool_calls = toolCalls
        messages.push(assistantMessage)

        if (!toolCalls.length) return finish({ status: 'done', data: response.content || '' })
        logDebug({
          kind: 'turn',
          pos: position,
          iteration,
          say: clipForLog(response.content, 500),
          calls: toolCalls.map((toolCall) => toolCall.function.name),
        })

        // 同一轮的调用彼此看不到结果，不存在返回值依赖；画布改动在 apply 内同步完成，可安全并发。
        const results = await Promise.all(toolCalls.map((toolCall) => runToolCall(toolCall, tools, emit, stopCallbacks)))
        if (controller.signal.aborted) return finish({ status: 'stopped' })
        // 同轮既有成功又有失败的 agent 结果时，失败优先
        const failed = results.find((result): result is AgentErrorResult => result instanceof AgentErrorResult)
        if (failed) return finish({ status: 'error', data: failed.message })
        const succeeded = results.find((result): result is AgentSuccessResult => result instanceof AgentSuccessResult)
        if (succeeded) return finish({ status: 'done', data: succeeded.data })

        toolCalls.forEach((toolCall, index) => {
          const limit = tools.find((tool) => tool.name === toolCall.function.name)?.resultLimit ?? TOOL_RESULT_LIMIT
          logDebug({
            kind: 'call',
            pos: position,
            name: toolCall.function.name,
            args: clipForLog(toolCall.function.arguments),
            result: clipForLog(results[index]!.toContent()),
          })
          messages.push({ role: 'tool', tool_call_id: toolCall.id, content: truncate(stringify(results[index]!.toContent()), limit) })
        })
      }
    } catch (error) {
      if (controller.signal.aborted) return finish({ status: 'stopped' })
      const err = error instanceof Error ? error : new Error(String(error))
      return finish({ status: 'error', data: err.message }, err)
    }
  }

  return { run, stop }
}

/** 跑一轮补全：把流式条目翻成事件下发，并返回本轮完整结果。 */
function runTurn(
  resourceScope: string,
  modelId: string,
  messages: AgentMessage[],
  tools: AgentTool[],
  emit: (payload: AgentPayload) => void,
  signal: AbortSignal,
): Promise<ChatCompletionResult> {
  return new Promise((resolve, reject) => {
    let result: ChatCompletionResult | null = null
    const startedToolIds = new Set<string>()
    const sink: Call<StreamItem> = {
      onNext: (item) => {
        if (item.type === 'delta') {
          if (item.content) emit({ type: 'narration', delta: item.content })
        } else if (item.type === 'reasoning') {
          if (item.content) emit({ type: 'reasoning', delta: item.content })
        } else if (item.type === 'tool_call') {
          if (!startedToolIds.has(item.id)) {
            startedToolIds.add(item.id)
            emit({ type: 'tool_start', id: item.id, name: item.name })
          }
          if (item.arguments) emit({ type: 'tool_args', id: item.id, delta: item.arguments })
        } else {
          result = item.result
        }
      },
      onComplete: (error) => {
        if (error) reject(error)
        else if (result) resolve(result)
        else reject(new Error('本轮结束但未收到完整结果'))
      },
    }
    chatCompletion(resourceScope, modelId, { messages, tools: toToolSchemas(tools) }, sink, signal)
  })
}

/** 执行单个工具调用，结果统一成 ToolResult；异常不抛出，转成 ErrorResult 让模型纠偏。 */
async function runToolCall(
  toolCall: ToolCall,
  tools: AgentTool[],
  emit: (payload: AgentPayload) => void,
  stopCallbacks: Array<() => void>,
): Promise<ToolResult> {
  const name = toolCall.function.name
  try {
    const args = toolCall.function.arguments ? (JSON.parse(toolCall.function.arguments) as Record<string, unknown>) : {}
    const tool = tools.find((candidate) => candidate.name === name)
    if (!tool) throw new Error(`未知工具: ${name}`)
    const executor = toExecutor(tool.apply(args))
    stopCallbacks.push(executor.cancel)
    const result = toToolResult(await executor.promise)
    const ok = !isFailureResult(result)
    emit({ type: 'tool_end', id: toolCall.id, ok, result: truncate(stringify(result.toContent()), RESULT_SUMMARY_LIMIT) })
    return result
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    emit({ type: 'tool_end', id: toolCall.id, ok: false, result: message })
    return new ErrorResult(message)
  }
}
