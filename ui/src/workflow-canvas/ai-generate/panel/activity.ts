import { ref } from 'vue'
import { v7 as uuidv7 } from 'uuid'
import { aggregators } from '@/conversation-panel/core/aggregators'
import type { AgentEvent } from '../type'

/**
 * 生成面板的活动：把扁平 AgentEvent 流（每条带 position）转成 conversation-panel 的内容项，
 * 由 ContentList 渲染，数据格式与对话流一致。
 * 用户每次发送的需求作为 QUESTION 项插在顶层；同一 position 的正文 / 思考增量续写到同一条 TEXT / REASONING；
 * 普通工具为平铺的 TOOL（相邻工具由 ContentList 折叠为 GROUP_TOOL）；
 * 委派工具为一个 GROUP，其起的子 agent 活动按 position 逐层包进 GROUP.children，经 aggregators 合并。
 * 内容项 id 用 uuid v7，与对话流一样按 id 排序即生成先后。
 */

/** conversation-panel 内容项（字段与 content/items/*.vue 读取的一致） */
export interface ContentItem {
  type: string
  id: string
  [field: string]: unknown
}

const TOOL_LABELS: Record<string, string> = {
  plan: '规划流程',
  get_canvas_detail: '查看画布',
  get_node_anchors: '查看节点出口',
  get_tools: '查询工具',
  add_node: '添加节点',
  add_edge: '添加连线',
  delete_node: '删除节点',
  delete_edge: '删除连线',
  configure_node: '配置节点',
  validate: '校验工作流',
  layout: '整理布局',
  submit_plan: '提交规划',
  get_field_options: '查看可引用变量',
  get_models: '查询模型',
  get_knowledge_list: '查询知识库',
  get_skill_resources: '查询技能资源',
  update: '写入配置',
  get_branches: '查看分支',
  add_branch: '新增分支',
  update_branch: '修改分支',
  delete_branch: '删除分支',
}

export function toolLabel(name: string) {
  return TOOL_LABELS[name] ?? name
}

/** 会起子 agent 的委派工具：展示为 GROUP，承载子 agent 活动 */
const DELEGATE_TOOLS = new Set(['plan', 'configure_node'])

/** 一次工具调用的本地记录：普通工具对应 TOOL 内容项，委派工具对应 GROUP */
interface ToolCall {
  tool: string
  contentId: string
  /** 发起调用的作用域（position 拼成的键） */
  scopeKey: string
  argumentsText: string
  delegate: boolean
  /** 委派 GROUP 已被子作用域认领 */
  claimed: boolean
}

function parseArgs(text: string): Record<string, unknown> | undefined {
  try {
    return JSON.parse(text || '{}') as Record<string, unknown>
  } catch {
    return undefined
  }
}

/** 工具标题：中文名，配置节点补节点 id，添加节点补名称 / 类型 */
function toolTitle(toolCall: ToolCall): string {
  const label = toolLabel(toolCall.tool)
  const args = parseArgs(toolCall.argumentsText)
  const hint = toolCall.tool === 'add_node' ? (args?.name ?? args?.type) : args?.nodeId
  return hint ? `${label} · ${String(hint)}` : label
}

/** 委派工具起的子作用域，其 position 末段的语义键 */
function spawnKeyOf(toolCall: ToolCall): string | undefined {
  if (toolCall.tool === 'configure_node') {
    const nodeId = parseArgs(toolCall.argumentsText)?.nodeId
    return typeof nodeId === 'string' ? nodeId : undefined
  }
  if (toolCall.tool === 'plan') return 'plan'
  return undefined
}

function tail(text: string) {
  const trimmed = text.trim()
  return trimmed.length > 40 ? `…${trimmed.slice(-40)}` : trimmed
}

function parentKeyOf(scopeKey: string) {
  const index = scopeKey.lastIndexOf('/')
  return index >= 0 ? scopeKey.slice(0, index) : ''
}

export function createActivity() {
  const activityItems = ref<ContentItem[]>([])
  const lastActivity = ref('')
  /** 子作用域 → 承载它的 GROUP id */
  const groupIdByScope = new Map<string, string>()
  const toolCallById = new Map<string, ToolCall>()
  /** 各作用域最后一条正文 / 思考：同类增量续写到同一项 */
  const lastStreamByScope = new Map<string, { type: 'TEXT' | 'REASONING'; id: string; text: string }>()

  function reset() {
    activityItems.value = []
    groupIdByScope.clear()
    toolCallById.clear()
    lastStreamByScope.clear()
    lastActivity.value = ''
  }

  /** 顶层按 id + type 合并；GROUP 分片经其聚合函数逐层合并 children */
  function mergeTop(chunk: ContentItem) {
    const aggregator = aggregators[chunk.type]
    const contents = activityItems.value
    const index = contents.findIndex((content) => content.id === chunk.id && content.type === chunk.type)
    if (index >= 0) contents[index] = aggregator ? aggregator(contents[index], chunk) : { ...contents[index], ...chunk }
    else contents.push(aggregator ? aggregator({}, chunk) : chunk)
  }

  /** 把分片按作用域链逐层包进 GROUP 外壳，再合并到顶层 */
  function emit(scopeKey: string, chunk: ContentItem) {
    ensureScope(scopeKey)
    let wrapped = chunk
    for (let key = scopeKey; key !== ''; key = parentKeyOf(key)) {
      wrapped = { type: 'GROUP', id: groupIdByScope.get(key)!, children: [wrapped] }
    }
    mergeTop(wrapped)
  }

  /** 本作用域的正文 / 思考到此为止：思考标为结束（思考卡随之收起），后续增量另起新项 */
  function settle(scopeKey: string) {
    const last = lastStreamByScope.get(scopeKey)
    if (!last) return
    lastStreamByScope.delete(scopeKey)
    if (last.type === 'REASONING') emit(scopeKey, { type: 'REASONING', id: last.id, status: 'SUCCESS' })
  }

  /**
   * 子作用域绑定到起它的委派 GROUP。同一节点可能被多次 configure_node，position 相同但属于不同轮委派：
   * 父作用域每出现一个尚未认领的匹配委派，就视为新一轮并改绑；找不到时单列一个以语义键为名的 GROUP 承载。
   */
  function ensureScope(scopeKey: string) {
    if (scopeKey === '') return
    const parentKey = parentKeyOf(scopeKey)
    const segment = scopeKey.slice(scopeKey.lastIndexOf('/') + 1)
    ensureScope(parentKey)
    const delegation = [...toolCallById.values()]
      .reverse()
      .find((toolCall) => toolCall.delegate && !toolCall.claimed && toolCall.scopeKey === parentKey && spawnKeyOf(toolCall) === segment)
    if (delegation) {
      delegation.claimed = true
      groupIdByScope.set(scopeKey, delegation.contentId)
      lastStreamByScope.delete(scopeKey)
      return
    }
    if (groupIdByScope.has(scopeKey)) return
    const groupId = uuidv7()
    groupIdByScope.set(scopeKey, groupId)
    settle(parentKey)
    emit(parentKey, { type: 'GROUP', id: groupId, name: segment, children: [] })
  }

  /** 用户发送的需求：顶层追加一条 QUESTION 项，之后的生成内容另起新项 */
  function pushQuestion(text: string) {
    settle('')
    mergeTop({ type: 'QUESTION', id: uuidv7(), content: text })
  }

  function pushEvent(event: AgentEvent) {
    const scopeKey = event.position.join('/')
    ensureScope(scopeKey)
    if (event.type === 'narration' || event.type === 'reasoning') {
      const type = event.type === 'narration' ? 'TEXT' : 'REASONING'
      let last = lastStreamByScope.get(scopeKey)
      if (last?.type !== type) {
        settle(scopeKey)
        last = { type, id: uuidv7(), text: '' }
        lastStreamByScope.set(scopeKey, last)
      }
      last.text += event.delta
      emit(scopeKey, { type, id: last.id, content: event.delta, ...(type === 'REASONING' ? { status: 'RUNNING' } : {}) })
      lastActivity.value = tail(last.text)
    } else if (event.type === 'tool_start') {
      settle(scopeKey)
      const delegate = DELEGATE_TOOLS.has(event.name)
      const toolCall: ToolCall = { tool: event.name, contentId: uuidv7(), scopeKey, argumentsText: '', delegate, claimed: false }
      toolCallById.set(event.id, toolCall)
      const name = toolLabel(event.name)
      emit(
        scopeKey,
        delegate
          ? { type: 'GROUP', id: toolCall.contentId, name, status: 'RUNNING', children: [] }
          : { type: 'TOOL', id: toolCall.contentId, name, arguments: '', content: '', status: 'RUNNING' },
      )
      lastActivity.value = name
    } else if (event.type === 'tool_args') {
      const toolCall = toolCallById.get(event.id)
      if (!toolCall) return
      toolCall.argumentsText += event.delta
      const name = toolTitle(toolCall)
      emit(
        toolCall.scopeKey,
        toolCall.delegate
          ? { type: 'GROUP', id: toolCall.contentId, name }
          : { type: 'TOOL', id: toolCall.contentId, name, arguments: event.delta },
      )
    } else if (event.type === 'tool_end') {
      const toolCall = toolCallById.get(event.id)
      if (!toolCall) return
      const status = event.ok ? 'SUCCESS' : 'FAIL'
      // 委派的返回值由子 agent 的正文体现；失败时把错误作为组内最后一条 FAILURE
      emit(
        toolCall.scopeKey,
        toolCall.delegate
          ? {
              type: 'GROUP',
              id: toolCall.contentId,
              status,
              children: event.ok ? [] : [{ type: 'FAILURE', id: uuidv7(), content: event.result }],
            }
          : { type: 'TOOL', id: toolCall.contentId, status, content: event.result },
      )
    } else if (event.type === 'done') {
      settle(scopeKey)
    } else if (event.type === 'error') {
      settle(scopeKey)
      // 子 agent 的失败已体现在其委派 GROUP 里，只有顶层失败单列一条错误
      if (scopeKey === '') emit('', { type: 'FAILURE', id: uuidv7(), content: event.message })
    }
  }

  return { activityItems, lastActivity, pushQuestion, pushEvent, reset }
}
