import { nextTick } from 'vue'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { compareList } from '@/workflow-canvas/config/constants'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { useAgentConfig } from '../common'
import type { AgentTool, JsonObjectSchema, JsonSchema, NodeAgentContext, NodeAgentModule, NodeReference, RunnableAgent } from '../type'
import {
  getDefaultModelConfig,
  getFieldOptions,
  getNode,
  nodeNameOf,
  nodeOutputFields,
  promptVariablesOf,
  readNodeData,
  validateReference,
  writeNodeProperties,
} from './canvas'
import { AgentSuccessResult, ErrorResult } from './result'

/**
 * 节点配置 agent 的装配与共用工具：各节点 agent.ts 经 useNodeAgent 组装，由节点 index.ts 的 agent 字段注册；
 * 另含实参处理、可引用变量查询、写入后校验收尾、update / validate 工具、模型来源、条件项与节点函数签名渲染。
 */

/** get_field_options 工具：本节点可引用的上游变量与提示词变量 */
export function getFieldOptionsTool(context: NodeAgentContext): AgentTool {
  return {
    name: 'get_field_options',
    description: '本节点可引用的上游变量：groups 为 [{nodeId, name, fields:[{value,label}]}]，promptVariables 为可直接写进提示词的变量。',
    parameters: { type: 'object', properties: {} },
    apply: () => ({ groups: getFieldOptions(context.lf, context.nodeId), promptVariables: promptVariablesOf(context.lf, context.nodeId) }),
  }
}

// ============================================================
// 实参
// ============================================================

/** 是否为单个引用 [节点ID, 字段] */
export function isReference(value: unknown): value is NodeReference {
  return Array.isArray(value) && value.length === 2 && value.every((item) => typeof item === 'string')
}

/** 某个形参的实参，统一为引用列表 */
export function argReferences(context: NodeAgentContext, name: string): NodeReference[] {
  const value = context.args[name]
  if (!value) return []
  return isReference(value) ? [value] : value
}

/** 某个形参的单个实参（只取第一个引用） */
export function argReference(context: NodeAgentContext, name: string): NodeReference | undefined {
  return argReferences(context, name)[0]
}

/** 引用在提示词里的写法：{{节点名称.字段}}，全局变量为 {{global.字段}} */
export function promptVariableOf(context: NodeAgentContext, [refNodeId, field]: NodeReference): string {
  if (refNodeId === 'global') return `{{global.${field}}}`
  const group = getFieldOptions(context.lf, context.nodeId).find((item) => item.nodeId === refNodeId)
  return `{{${group?.name ?? refNodeId}.${field}}}`
}

/** 已绑定实参的说明，写进节点配置 agent 的 prompt */
function describeArgs(context: NodeAgentContext): string {
  const lines = Object.keys(context.args).map((name) => {
    const references = argReferences(context, name).map((reference) => `${JSON.stringify(reference)}（提示词写作 ${promptVariableOf(context, reference)}）`)
    return `- ${name} = ${references.join('、')}`
  })
  return lines.length ? `已绑定入参（由父 agent 连线决定，需要引用上游数据时使用这些，不要另选）：\n${lines.join('\n')}` : '本节点没有绑定入参。'
}

// ============================================================
// 写入后校验收尾
// ============================================================

type ValidationError = { node?: { properties?: { stepName?: string } }; errMessage?: unknown }

/** 把节点 validate() 的拒绝原因（el-form 字段错误或文本）整理为可读文本 */
export function formatValidationError(error: unknown): string {
  const { node, errMessage } = (error ?? {}) as ValidationError
  const prefix = node?.properties?.stepName ? `${node.properties.stepName}：` : ''
  if (typeof errMessage === 'string') return prefix + errMessage
  if (errMessage && typeof errMessage === 'object') {
    const messages = Object.values(errMessage as Record<string, Array<{ message?: string }>>)
      .flat()
      .map((item) => item?.message)
      .filter(Boolean)
    if (messages.length) return prefix + messages.join('；')
  }
  return prefix + (typeof error === 'string' ? error : JSON.stringify(errMessage ?? error))
}

export function summarizeNodeData(value: unknown): unknown {
  const text = JSON.stringify(value ?? {})
  return text.length > 600 ? `${text.slice(0, 600)}…` : value
}

/**
 * 调用节点视图注册的 validate()（表单必填与引用有效性），与发布前校验同一套规则。
 * 等两次 nextTick，让表单先按新写入的 node_data 渲染；节点未挂载表单时视为通过。
 */
export async function runNodeValidate(context: NodeAgentContext): Promise<string | null> {
  await nextTick()
  await nextTick()
  const node = getNode(context.lf, context.nodeId) as (ReturnType<typeof getNode> & { validate?: () => Promise<unknown> }) | undefined
  if (!node) return `节点不存在: ${context.nodeId}`
  try {
    await node.validate?.()
    return null
  } catch (error) {
    return formatValidationError(error)
  }
}

/**
 * 校验通过即交卷（stop），交付节点配置后的真实输出字段（config.fields，与变量选择器一致），
 * 父 agent 据此接下游；不通过返回 ErrorResult 让模型续修。
 */
export async function finishWithValidate(context: NodeAgentContext): Promise<AgentSuccessResult | ErrorResult> {
  const error = await runNodeValidate(context)
  if (error) return new ErrorResult(`节点校验未通过：${error}`)
  const node = getNode(context.lf, context.nodeId)
  const outputs = node ? nodeOutputFields(node) : []
  // 父 agent 要求的动态返回字段必须产出，下游才能按约定引用
  const missing = context.expectedReturns.filter((field) => !outputs.some((output) => output.value === field))
  if (missing.length) return new ErrorResult(`缺少要求产出的返回字段：${missing.join('、')}，请按要求补充后重新写入`)
  return new AgentSuccessResult({ outputs })
}

/** update 工具：apply 写入节点（返回错误文本或 null），写入成功后自动校验并以 stop 收尾 */
export function createUpdateTool(
  context: NodeAgentContext,
  config: JsonObjectSchema,
  apply: (args: Record<string, unknown>) => string | null | Promise<string | null>,
  description = '写入本节点配置；写入后自动校验，通过即配置完成。',
): AgentTool {
  return {
    name: 'update',
    description,
    parameters: config,
    apply: async (args) => {
      if (!getNode(context.lf, context.nodeId)) return new ErrorResult(`节点不存在: ${context.nodeId}`)
      const error = await apply(args)
      if (error) return new ErrorResult(error)
      return finishWithValidate(context)
    },
  }
}

/** validate 工具：分支类节点逐个增改删后调用它校验收尾 */
export function createValidateTool(context: NodeAgentContext): AgentTool {
  return {
    name: 'validate',
    description: '全部配置完成后调用：校验本节点配置，通过即配置完成、任务结束；不通过返回 error 继续修。',
    parameters: { type: 'object', properties: {} },
    apply: () => finishWithValidate(context),
  }
}

// ============================================================
// 模型来源
// ============================================================

/** 模型字段：default=使用工作流默认模型，否则为 get_models 返回的模型 id */
export const MODEL_FIELD_SCHEMA = {
  type: 'string',
  description: '模型："default" 表示使用工作流默认模型（已配置时首选）；否则传 get_models 返回的模型 id',
}

/** 节点的模型槽位：模型类型与写入 node_data 的字段名（与 NodeModelSelect 的 fields 一致） */
export interface ModelSlot {
  type: string
  label: string
  fields: { source: string; id: string; reference: string }
}

/** 按模型类型与字段前缀生成模型槽位，如 STT 节点的前缀为 stt_model */
export function modelSlot(type: string, label: string, prefix = 'model'): ModelSlot {
  return { type, label, fields: { source: `${prefix}_id_type`, id: `${prefix}_id`, reference: `${prefix}_id_reference` } }
}

export const LLM_MODEL = modelSlot('LLM', '大语言模型')

/** 把模型参数解析为节点的模型字段（来源 / 模型 id / 引用） */
export function resolveModelFields(context: NodeAgentContext, model: unknown, slot: ModelSlot = LLM_MODEL): Record<string, unknown> | string {
  const { source, id, reference } = slot.fields
  if (model === undefined || model === null || model === '' || model === 'default') {
    if (!getDefaultModelConfig(context.lf, slot.type)?.model_id) {
      return `当前工作流未配置默认${slot.label}（${slot.type}），请先 get_models 选择一个模型 id`
    }
    return { [source]: 'default', [id]: '', [reference]: [] }
  }
  return { [source]: 'custom', [id]: String(model), [reference]: [] }
}

/** 列出可用模型：经工作流 Store 按画布资源范围查询（与节点模型下拉共用缓存），并告知默认模型是否已配置 */
export function getModelsTool(context: NodeAgentContext, slot: ModelSlot = LLM_MODEL): AgentTool {
  return {
    name: 'get_models',
    description: `列出可用的${slot.label}（${slot.type}），返回 { defaultConfigured, models:[{id,name,provider}] }。defaultConfigured=true 时优先用 "default"。`,
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const models = await useWorkflowStore(context.bindings.resourceScope).getModelListWithShared({ model_type: slot.type })
      return {
        defaultConfigured: !!getDefaultModelConfig(context.lf, slot.type)?.model_id,
        models: models.map((model) => ({ id: model.id, name: model.name, provider: model.provider, model_name: model.model_name })),
      }
    },
  }
}

// ============================================================
// 知识库
// ============================================================

let knowledgeCache: Promise<KnowledgeItem[]> | undefined

/** 当前工作空间的知识库（缓存，失败时清掉以便重试） */
export const loadKnowledge = () =>
  (knowledgeCache ??= KnowledgeApi.getAllKnowledge().catch((error) => {
    knowledgeCache = undefined
    throw error
  }))

export const getKnowledgeListTool: AgentTool = {
  name: 'get_knowledge_list',
  description: '列出当前工作空间的知识库 [{id,name,desc,embedding_model_id}]。同一检索节点只能选向量模型相同的知识库。',
  parameters: { type: 'object', properties: {} },
  apply: async () =>
    (await loadKnowledge()).map((knowledge) => ({
      id: knowledge.id,
      name: knowledge.name,
      desc: knowledge.desc,
      embedding_model_id: knowledge.embedding_model_id,
    })),
}

// ============================================================
// 条件项
// ============================================================

export const VALUE_LESS_COMPARES = ['is_null', 'is_not_null', 'is_true', 'is_not_true']

/** 条件项 schema：判断器分支、Break/Continue 条件共用 */
export const CONDITION_SCHEMA = {
  type: 'object',
  properties: {
    field: { type: 'array', items: { type: 'string' }, description: '被比较的变量 [节点ID, 字段]，从 get_field_options 取' },
    compare: {
      type: 'string',
      enum: compareList.map((item) => item.value),
      description: compareList.map((item) => `${item.value}=${item.label}`).join('，'),
    },
    value: { type: 'string', description: '比较值；为空/不为空/为真/不为真无需比较值' },
  },
  required: ['field', 'compare'],
}

export interface ConditionItem {
  field: string[]
  compare: string
  value: string | number
}

/** 规整并校验条件列表；返回错误文本或规整后的列表 */
export function normalizeConditions(context: NodeAgentContext, raw: unknown, label: string): ConditionItem[] | string {
  if (!Array.isArray(raw)) return `${label} 应为数组`
  const conditions: ConditionItem[] = []
  for (const [index, item] of raw.entries()) {
    const condition = item as Partial<ConditionItem>
    const error = validateReference(context.lf, context.nodeId, condition.field, `${label}[${index}].field`)
    if (error) return error
    if (!compareList.some((compare) => compare.value === condition.compare)) return `${label}[${index}].compare 不合法：${condition.compare}`
    const compare = String(condition.compare)
    conditions.push({
      field: (condition.field as unknown[]).map(String),
      compare,
      // 无比较值的运算沿用节点协议写入占位值 1
      value: VALUE_LESS_COMPARES.includes(compare) ? 1 : String(condition.value ?? ''),
    })
  }
  return conditions
}

// ============================================================
// 节点配置 agent 装配
// ============================================================

const NODE_GUIDE = `你是 MaxKB 工作流某个节点的配置专家，只配置已绑定的这一个节点，不改动画布结构。
节点被当作一个函数：入参（上游数据）已由父 agent 绑定，你只负责配置（模型、提示词、资源、阈值、分支等常量）。
工作方式：
1. 需要引用上游数据时使用下方「已绑定入参」；提示词里按其给出的 {{节点名称.字段}} 写法原样使用。get_field_options 可查看全部可引用变量，仅在入参未覆盖时参考。
2. 需要选资源（模型、知识库等）时用对应查询工具拿真实 id，不要猜。
3. 写入配置后系统会自动做节点校验：通过即配置完成、任务结束；返回 error 就按提示修正后重试。`

/** 节点配置 agent 骨架：通用指引 + 节点专属 prompt + 已绑定入参与要求产出的返回字段，工具前置 get_field_options */
export function useNodeAgent(context: NodeAgentContext, config: { prompt: string; tools: AgentTool[] }): RunnableAgent {
  const node = getNode(context.lf, context.nodeId)
  const expected = context.expectedReturns.length ? `\n要求产出的返回字段（字段名必须一致）：${context.expectedReturns.join('、')}` : ''
  return useAgentConfig(
    {
      prompt: `${NODE_GUIDE}\n\n${config.prompt}\n\n本节点：id=${context.nodeId}，名称=${node ? nodeNameOf(node) : context.nodeId}\n${describeArgs(context)}${expected}`,
      tools: [getFieldOptionsTool(context), ...config.tools],
    },
    context.bindings,
  )
}

/** Break / Continue 共用的条件配置 agent */
export function createLoopConditionAgent(type: WorkflowNodeType.LoopBreakNode | WorkflowNodeType.LoopContinueNode, label: string): NodeAgentModule {
  const config: JsonObjectSchema = {
    type: 'object',
    properties: {
      condition: { type: 'string', enum: ['and', 'or'], description: '多条条件之间：and 全部满足 / or 任一满足' },
      conditions: { type: 'array', items: CONDITION_SCHEMA, description: '条件列表，为空表示无条件执行' },
    },
    required: ['conditions'],
  }
  return {
    description:
      type === WorkflowNodeType.LoopBreakNode
        ? '相当于循环里的 if (...) break：满足条件时跳出循环，条件为空则无条件跳出；仅循环体内可用，无限循环（LOOP）必须放一个'
        : '相当于循环里的 if (...) continue：满足条件时跳过本轮剩余节点、进入下一轮；仅循环体内可用',
    params: {
      type: 'object',
      properties: {
        fields: { type: 'array', items: {}, description: '条件里被比较的变量，常用 loop-start-node 的 index / item' },
      },
    },
    config,
    returns: { type: 'object', properties: {}, additionalProperties: false },
    useAgent: (context) =>
      useNodeAgent(context, {
        prompt: [
          `${type}（${label}）配置要点：`,
          '- conditions 为空表示无条件执行；条件 field 使用已绑定入参 fields 中的引用。',
          '- condition：多条条件之间 and（全部满足）/ or（任一满足）。',
        ].join('\n'),
        tools: [
          createUpdateTool(context, config, (args) => {
            const node = getNode(context.lf, context.nodeId)!
            const conditions = normalizeConditions(context, args.conditions ?? [], 'conditions')
            if (typeof conditions === 'string') return conditions
            writeNodeProperties(node, {
              node_data: {
                ...readNodeData<Record<string, unknown>>(node),
                condition: args.condition === 'or' ? 'or' : 'and',
                condition_list: conditions,
              },
            })
            return null
          }),
        ],
      }),
  }
}

// ============================================================
// 节点函数签名
// ============================================================

/** JSON Schema 渲染成 TS 风格的类型 */
function schemaType(schema: JsonSchema | undefined): string {
  if (!schema) return 'any'
  if (Array.isArray(schema.enum)) return schema.enum.map((value) => JSON.stringify(value)).join(' | ')
  if (schema.type === 'array') return `${schemaType(schema.items as JsonSchema | undefined)}[]`
  return typeof schema.type === 'string' ? schema.type : 'any'
}

function fieldLine(name: string, schema: JsonSchema, optional: boolean): string {
  const description = typeof schema.description === 'string' ? ` /* ${schema.description} */` : ''
  return `${name}${optional ? '?' : ''}: ${schemaType(schema)}${description}`
}

/** 对象 schema 的字段列表；additionalProperties 渲染为索引签名 */
function objectFields(schema: JsonObjectSchema, indexName: string): string[] {
  const required = new Set(schema.required ?? [])
  const fields = Object.entries(schema.properties).map(([name, property]) => fieldLine(name, property, !required.has(name)))
  const extra = schema.additionalProperties
  if (extra && typeof extra === 'object') fields.push(fieldLine(`[${indexName}]`, extra, false))
  return fields
}

/** 配置项只列名称与说明的首句，控制目录篇幅 */
function configSummary(schema: JsonObjectSchema): string {
  const items = Object.entries(schema.properties).map(([name, property]) => {
    const description = typeof property.description === 'string' ? property.description.split(/[，；。,;]/)[0] : ''
    return description ? `${name}（${description}）` : name
  })
  return items.join('、') || '无'
}

/**
 * 把节点渲染成函数签名，供建图 agent 像组合函数一样设计画布：
 * // 名称：说明
 * // 配置：配置项
 * type(形参): { 返回字段 }
 */
export function renderNodeFunction(type: string, label: string, module: NodeAgentModule): string {
  const params = objectFields(module.params, '参数名')
  const returns = objectFields(module.returns, '字段名')
  return [
    `// ${label}：${module.description}`,
    `// 配置：${configSummary(module.config)}`,
    `${type}(${params.join(', ')}): ${returns.length ? `{ ${returns.join('; ')} }` : 'void'}`,
  ].join('\n')
}
