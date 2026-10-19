import type LogicFlow from '@logicflow/core'
import type { ChatCompletionMessage } from '@/api/types'
import type { WorkflowMode } from '@/workflow-canvas/types'

/**
 * 工作流 AI 生成的类型定义（纯类型）。
 * 运行引擎在 create-agent.ts，SSE 与 agent 装配在 common.ts，画布适配在 tools/canvas.ts，
 * 建图工具在 tools/index.ts，节点配置 agent 在各节点目录的 agent.ts，画布父 agent 在 application.ts。
 */

// ============================================================
// 流式补全
// ============================================================

export interface ToolCall {
  id: string
  type: string
  function: { name: string; arguments: string }
}

export interface ChatCompletionResult {
  content: string
  toolCalls: ToolCall[]
  finishReason: string | null
  usage?: Record<string, unknown> | null
  /** thinking 模型的思考内容及其原始字段名（回传 assistant 消息时按原字段名带回） */
  reasoningKey?: string | null
  reasoningContent?: string | null
}

/** 流式订阅者：onNext 逐条收条目，onComplete 收尾（error 有值即失败）。 */
export interface Call<T> {
  onNext(item: T): void
  onComplete?(error?: Error): void
}

/**
 * 后端一轮流式补全逐条下发的条目：
 * - delta / reasoning：增量文本
 * - tool_call：某工具调用的一个片段（id + name + 本片 arguments 增量）
 * - completion：整轮最终结果（累积后的完整 toolCalls）
 */
export type StreamItem =
  | { type: 'delta'; content: string }
  | { type: 'reasoning'; content: string }
  | { type: 'tool_call'; id: string; name: string; arguments: string }
  | { type: 'completion'; result: ChatCompletionResult }

export interface SseEvent {
  type: 'delta' | 'reasoning' | 'tool_call' | 'completion' | 'error'
  [key: string]: unknown
}

/** agent 历史消息：OpenAI 格式，assistant 可按原字段名携带思考内容。 */
export type AgentMessage = ChatCompletionMessage & Record<string, unknown>

// ============================================================
// Agent 事件 / 工具 / 绑定
// ============================================================

/**
 * createAgent 对外下发的事件负载：
 * - narration / reasoning：assistant 正文 / 思考的增量文本
 * - tool_start / tool_args / tool_end：工具卡的建立、入参增量与执行结果
 * - done / error：本 agent 终态，done.data 为本 agent 交付
 */
export type AgentPayload =
  | { type: 'narration'; delta: string }
  | { type: 'reasoning'; delta: string }
  | { type: 'tool_start'; id: string; name: string }
  | { type: 'tool_args'; id: string; delta: string }
  | { type: 'tool_end'; id: string; ok: boolean; result: string }
  | { type: 'done'; data?: unknown }
  | { type: 'error'; message: string }

/**
 * 一条对外事件 = 负载 + position（从事件树根到所属 agent 的语义键链）。
 * 顶层 agent 为 []，委派工具起的子 agent 在父 position 后追加语义键（节点 id、'plan'、'validate'）。
 */
export type AgentEvent = AgentPayload & { position: string[] }

/** 可取消的工具执行：委派型工具返回它，父 agent 停止时级联 cancel。 */
export interface Executor {
  promise: Promise<unknown>
  cancel: () => void
}

/** 模型可调用的一个函数。 */
export interface AgentTool {
  /** 函数名（下发给模型的 tool 名） */
  name: string
  description: string
  /** 参数 JSON Schema */
  parameters: Record<string, unknown>
  /** 执行体：只接收模型给的 args，其余上下文在构造期闭包 */
  apply: (args: Record<string, unknown>) => unknown | Promise<unknown> | Executor
  /** 结果回喂模型的截断上限（字符），缺省走全局上限 */
  resultLimit?: number
}

/** 构造期绑定：装配 agent 与建工具时使用的上下文。 */
export interface AgentBindings {
  /** 主画布 LogicFlow 实例；循环体画布经 lf_id 从主画布展开 */
  rootLf: LogicFlow
  /** 模型 id（委派的子 agent 复用同一模型） */
  modelId: string
  /** 对外事件出口 */
  call: Call<AgentEvent>
  /** 主画布模式 */
  workflowMode: WorkflowMode
  /** 画布资源范围（workspace 等），资源查询经 useWorkflowStore(resourceScope) */
  resourceScope: string
  /** 画布所属资源 id（应用 / 工具 / 知识库），MCP 等按资源查询的接口使用 */
  resourceId?: string
  /** 事件树层级路径（顶层=[]） */
  position?: string[]
  /** 循环轮次上限 */
  maxIterations?: number
  /** 本次生成的整体目标（用户需求），折进各层 system 作背景 */
  context?: string
  /** 本 agent 的消息历史（活引用）；委派时传入从父裁出的初始历史 */
  messages?: AgentMessage[]
}

/** 一台 agent 的声明式配置。 */
export interface AgentConfig {
  prompt: string
  tools: AgentTool[]
}

/** 装配好、可交给 createAgent 运行的 agent。 */
export interface RunnableAgent {
  prompt: string
  messages: AgentMessage[]
  tools: AgentTool[]
  modelId: string
  /** 画布资源范围，补全请求经 useWorkflowStore(resourceScope) 发起 */
  resourceScope: string
  call: Call<AgentEvent>
  position: string[]
  maxIterations: number
}

/** 一次 run 的终态结果。 */
export interface AgentResult {
  status: 'done' | 'error' | 'stopped'
  /** 隐式结束为最后一段正文；终止工具结束为其交出的结构化数据 */
  data?: unknown
}

export interface AgentHandle {
  /** 追加一条 user 消息并循环到终态；非重入 */
  run: (requirement: string) => Promise<AgentResult>
  /** 中断在途请求并级联停止委派中的子 agent */
  stop: () => void
}

// ============================================================
// 节点配置 agent
// ============================================================

/** JSON Schema（OpenAI function calling 的 parameters 格式） */
export type JsonSchema = Record<string, unknown>

/**
 * 对象形 JSON Schema：节点的 params / config / returns 统一使用。
 * 框架扩展字段（渲染给模型时去掉）：
 * - params 属性上的 x-bind：实参由框架直接写入 node_data 的该字段；未声明则交由节点配置 agent 使用；
 * - returns.additionalProperties 上的 x-from：动态返回字段来自哪一项配置。
 */
export interface JsonObjectSchema {
  [key: string]: unknown
  type: 'object'
  properties: Record<string, JsonSchema>
  required?: string[]
  additionalProperties?: boolean | JsonSchema
}

/** 实参：对上游输出的引用 [节点ID, 字段]，如 ['start-node', 'question'] */
export type NodeReference = [string, string]

/** 节点配置 agent 运行时的上下文 */
export interface NodeAgentContext {
  /** 被配置节点所在画布 */
  lf: LogicFlow
  /** 被配置节点 id */
  nodeId: string
  /** 所在画布模式（主画布 Application，循环体 ApplicationLoop） */
  workflowMode: WorkflowMode
  /** 本节点配置 agent 的绑定（position 已追加节点 id） */
  bindings: AgentBindings
  /** 父 agent 传入并已校验的实参：形参名 → 引用（可多个） */
  args: Record<string, NodeReference | NodeReference[]>
  /** 父 agent 写的配置要求 */
  requirement: string
  /** 父 agent 要求产出的动态返回字段名 */
  expectedReturns: string[]
}

/**
 * 节点 agent.ts 的默认导出：把节点当作一个函数暴露给建图 agent，由节点 index.ts 的 agent 字段注册。
 * params / config / returns 均为 JSON Schema：
 * - description 为函数说明：做什么、何时用、与上下游怎么配合；
 * - params 为形参：运行时由上游提供，实参为引用 [节点ID, 字段]，由父 agent 连线决定；
 * - config 为配置：搭画布时确定的常量，由节点配置 agent 按 requirement 决定，同时作为其 update 工具的 parameters；
 * - returns 为返回：固定字段写在 properties，由配置生成的字段用 additionalProperties 说明（无则为 false）；
 * - useAgent 装配节点配置 agent：只负责配置，形参已由框架绑定；通过校验后交付真实输出字段（config.fields）。
 */
export interface NodeAgentModule {
  description: string
  params: JsonObjectSchema
  config: JsonObjectSchema
  returns: JsonObjectSchema
  useAgent: (context: NodeAgentContext) => RunnableAgent
}
