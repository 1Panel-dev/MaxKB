import { pick } from 'lodash'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem } from '@/api/types'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, getModelsTool, MODEL_FIELD_SCHEMA, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { AgentTool, JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import type { AiChatNodeForm, ToolResourceOption } from './types'

/**
 * ai-chat-node（AI 对话）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准。
 * 入参（提示词素材、图片、视频）由父 agent 绑定；config 即 update 的参数，写入并校验通过后交付节点的输出字段（config.fields）。
 * 关联应用（application_ids）与自定义 MCP 服务（mcp_servers）暂不由 AI 配置。
 */

/** 节点「工具」可选的工具类型，与资源设置的工具选择弹窗一致；Skills 与 MCP 各自单列 */
const NODE_TOOL_TYPES: string[] = [TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW, TOOL_TYPE.INTERNAL]

const ID_LIST_SCHEMA = (description: string) => ({ type: 'array', items: { type: 'string' }, description })

interface SkillResources {
  tools: ToolItem[]
  skills: ToolItem[]
  mcps: ToolItem[]
}

/** 节点可挂载的技能资源：工具、Skills、MCP，均只取已启用的 */
async function loadSkillResources(context: NodeAgentContext): Promise<SkillResources> {
  const store = useWorkflowStore(context.bindings.resourceScope)
  const [toolGroups, skills, mcps] = await Promise.all([
    Promise.all(NODE_TOOL_TYPES.map((toolType) => store.getToolListWithShared({ tool_type: toolType }))),
    store.getToolListWithShared({ tool_type: TOOL_TYPE.SKILL }),
    store.getToolListWithShared({ tool_type: TOOL_TYPE.MCP }),
  ])
  const activeOf = (resources: ToolItem[], toolTypes: string[]) =>
    resources.filter((resource) => resource.is_active && toolTypes.includes(resource.tool_type))
  return {
    tools: activeOf(toolGroups.flat(), NODE_TOOL_TYPES),
    skills: activeOf(skills, [TOOL_TYPE.SKILL]),
    mcps: activeOf(mcps, [TOOL_TYPE.MCP]),
  }
}

/** 把模型给的 id 列表对照真实资源，返回节点回显用的快照；有不存在的 id 时返回错误文本 */
function resolveResources(ids: unknown, resources: ToolItem[], label: string): ToolResourceOption[] | string {
  if (!Array.isArray(ids)) return `${label} 应为 id 数组`
  const missingIds = ids.filter((id) => !resources.some((resource) => resource.id === id))
  if (missingIds.length) return `${label} 中的 ${missingIds.join('、')} 不存在或未启用，先 get_skill_resources 查询`
  return ids.map((id) => pick(resources.find((resource) => resource.id === id)!, ['desc', 'icon', 'id', 'name', 'source', 'tool_type']))
}

function skillResourcesTool(context: NodeAgentContext): AgentTool {
  return {
    name: 'get_skill_resources',
    description: '列出可挂到本节点的技能资源：tools（工具）、skills（Skills）、mcps（MCP），均为 [{id,name,desc}]。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const { tools, skills, mcps } = await loadSkillResources(context)
      const brief = (resources: ToolItem[]) => resources.map(({ id, name, desc }) => ({ id, name, desc }))
      return { tools: brief(tools), skills: brief(skills), mcps: brief(mcps) }
    },
  }
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    materials: { type: 'array', items: {}, description: '提示词素材：用户问题、检索结果、上游输出等，写进提示词' },
    images: { type: 'array', description: '要识别的图片', 'x-bind': 'image_list' },
    videos: { type: 'array', description: '要识别的视频', 'x-bind': 'video_list' },
  },
  required: ['materials'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    system: { type: 'string', description: '系统提示词（角色设定），写清身份、目标、回答规范与限制' },
    prompt: { type: 'string', description: '用户提示词，以 {{节点名称.字段}} 写入入参 materials' },
    dialogue_number: { type: 'number', description: '携带的历史对话轮数，0 表示不带历史，默认 1' },
    dialogue_type: { type: 'string', enum: ['WORKFLOW', 'NODE'], description: '历史来源：WORKFLOW 工作流问答（默认），NODE 本节点问答' },
    is_result: { type: 'boolean', description: '是否把回答输出给用户：最终回答为 true，中间加工为 false' },
    vision: { type: 'boolean', description: '是否开启视觉（识别图片 / 视频），绑定了入参 images / videos 时默认开启' },
    tool_ids: ID_LIST_SCHEMA('挂载的工具 id 列表（get_skill_resources.tools），传空数组表示清空'),
    skill_tool_ids: ID_LIST_SCHEMA('挂载的 Skills id 列表（get_skill_resources.skills），传空数组表示清空'),
    mcp_tool_ids: ID_LIST_SCHEMA('挂载的 MCP id 列表（get_skill_resources.mcps），传空数组表示清空'),
    mcp_output_enable: { type: 'boolean', description: '是否输出技能的执行过程，默认 true' },
    reasoning_content_enable: { type: 'boolean', description: '是否输出思考过程（仅思考模型需要）' },
  },
  required: ['model', 'prompt'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    answer: { type: 'string', description: '回答内容' },
    reasoning_content: { type: 'string', description: '思考过程（开启输出思考时有值）' },
    history_message: { type: 'array', description: '本节点的历史消息' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'ai-chat-node（AI 对话）配置要点：',
      '- model：工作流已配置默认模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- system：角色设定，写清身份、目标、回答规范与限制（按用户需求生成完整内容，不要留占位）。',
      '- prompt：用户提示词，必填，按已绑定入参 materials 给出的 {{节点名称.字段}} 写法引用素材；基于检索时同时引用检索结果与用户问题。',
      '- dialogue_number / dialogue_type：携带的历史对话轮数（0 表示不带历史）；历史来源 WORKFLOW 为整个工作流的问答，NODE 为本节点自己的问答。',
      '- is_result：是否把回答输出给用户；作为流程最终回答时为 true，作为中间加工步骤时为 false。',
      '- vision：图片 / 视频已由入参 images / videos 绑定，绑定时默认开启视觉，无需配置。',
      '- tool_ids / skill_tool_ids / mcp_tool_ids：需求要求节点调用工具、Skills 或 MCP 时，先 get_skill_resources 取真实 id 再挂载；不需要时不传。',
      '- mcp_output_enable：是否把技能的执行过程输出给用户，默认 true。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前 AI 对话节点：模型、系统/用户提示词、历史对话、是否输出给用户、视觉、技能（工具 / Skills / MCP）、是否输出思考过程。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const modelFields = resolveModelFields(context, args.model)
          if (typeof modelFields === 'string') return new ErrorResult(modelFields)
          const promptError =
            validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt') ??
            validatePromptVariables(context.lf, context.nodeId, args.system, 'system')
          if (promptError) return new ErrorResult(promptError)
          const nodeData = readNodeData<Partial<AiChatNodeForm>>(node)

          // 视觉：绑定了图片 / 视频入参时默认开启
          const hasMedia = !!(argReference(context, 'images') || argReference(context, 'videos'))
          const visionFields: Partial<AiChatNodeForm> = {
            vision: typeof args.vision === 'boolean' ? args.vision : (nodeData.vision || hasMedia),
          }

          // 技能挂载：id 对照真实资源，同时写回节点回显所需的快照
          const skillFields: Partial<AiChatNodeForm> = {}
          if (args.tool_ids !== undefined || args.skill_tool_ids !== undefined || args.mcp_tool_ids !== undefined) {
            const resources = await loadSkillResources(context)
            if (args.tool_ids !== undefined) {
              const tools = resolveResources(args.tool_ids, resources.tools, 'tool_ids')
              if (typeof tools === 'string') return new ErrorResult(tools)
              Object.assign(skillFields, { tool_ids: tools.map(({ id }) => id), tool_list: tools })
            }
            if (args.skill_tool_ids !== undefined) {
              const skills = resolveResources(args.skill_tool_ids, resources.skills, 'skill_tool_ids')
              if (typeof skills === 'string') return new ErrorResult(skills)
              Object.assign(skillFields, { skill_tool_ids: skills.map(({ id }) => id), skill_tool_list: skills })
            }
            if (args.mcp_tool_ids !== undefined) {
              const mcps = resolveResources(args.mcp_tool_ids, resources.mcps, 'mcp_tool_ids')
              if (typeof mcps === 'string') return new ErrorResult(mcps)
              Object.assign(skillFields, { mcp_tool_ids: mcps.map(({ id }) => id), mcp_source: 'referencing' })
            }
          }

          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...modelFields,
              ...visionFields,
              ...skillFields,
              system: typeof args.system === 'string' ? args.system : (nodeData.system ?? ''),
              prompt: String(args.prompt ?? nodeData.prompt ?? ''),
              dialogue_number: Number(args.dialogue_number ?? nodeData.dialogue_number ?? 1),
              dialogue_type: args.dialogue_type === 'NODE' || args.dialogue_type === 'WORKFLOW' ? args.dialogue_type : (nodeData.dialogue_type ?? 'WORKFLOW'),
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? true),
              mcp_output_enable: typeof args.mcp_output_enable === 'boolean' ? args.mcp_output_enable : (nodeData.mcp_output_enable ?? true),
              model_setting: {
                reasoning_content_start: '<think>',
                reasoning_content_end: '</think>',
                ...nodeData.model_setting,
                reasoning_content_enable:
                  typeof args.reasoning_content_enable === 'boolean'
                    ? args.reasoning_content_enable
                    : !!nodeData.model_setting?.reasoning_content_enable,
              },
            },
          })
          // 写入后自动校验：通过返回 AgentSuccessResult 交付输出字段并结束，不通过返回 ErrorResult 让模型续修
          return finishWithValidate(context)
        },
      },
      getModelsTool(context),
      skillResourcesTool(context),
    ],
  })
}

export default {
  description:
    '调用大模型生成回答，可流式输出给用户，可挂载工具 / Skills / MCP。面向用户的最终回答 is_result=true，中间加工步骤为 false；' +
    '基于知识库回答时提示词同时引用检索结果 data 与用户问题，并要求仅依据已知信息作答；后一步加工时引用前一步的 answer',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
