/** 简易智能体设置草稿与 v2 详情字段的回填。 */
import { cloneDeep } from 'lodash'
import type { ApplicationDetail, ApplicationFormPayload, KnowledgeItem, ToolItem } from '@/api/types'

export const DEFAULT_DESIGNATED_ANSWER = '你好，我是 XXX 小助手，我的知识库只包含了 XXX 产品相关知识，请重新描述您的问题。'

export const DEFAULT_PROBLEM_OPTIMIZATION_PROMPT =
  '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中'

export interface ModelSetting extends Record<string, unknown> {
  system: string
  prompt: string
  no_references_prompt: string
  reasoning_content_enable: boolean
  reasoning_content_start: string
  reasoning_content_end: string
}
export interface KnowledgeSetting extends Record<string, unknown> {
  search_mode: string
  top_n: number
  similarity: number
  max_paragraph_char_number: number
  no_references_setting: { status: string; value: string }
}
export interface ApplicationSettings extends ApplicationFormPayload {
  name: string
  desc: string
  model_id: string
  dialogue_number: number
  prologue: string
  model_setting: ModelSetting
  knowledge_setting: KnowledgeSetting
  knowledge_id_list: string[]
  application_ids: string[]
  tool_ids: string[]
  skill_tool_ids: string[]
  mcp_tool_ids: string[]
  mcp_source: 'custom' | 'referencing'
  mcp_servers: string
  mcp_output_enable: boolean
  application_list?: (Partial<ApplicationDetail> & { id: string })[]
  tool_list?: (Partial<ToolItem> & { id: string })[]
  skill_tool_list?: (Partial<ToolItem> & { id: string })[]
  model_params_setting: Record<string, unknown>
  stt_model_id: string
  stt_model_params_setting: Record<string, unknown>
  tts_model_id: string
  tts_model_params_setting: Record<string, unknown>
  long_term_model_id: string
  long_term_model_params_setting: Record<string, unknown>
  long_term_trigger_setting: Record<string, unknown>
  long_term_trigger_type: 'ROUND' | 'SCHEDULED'
}
/** 简易智能体长期记忆只保存具体模型和触发配置。 */
export type LongTermSettingData = Pick<
  ApplicationSettings,
  'long_term_model_id' | 'long_term_model_params_setting' | 'long_term_trigger_setting' | 'long_term_trigger_type'
>

export type SelectedKnowledge = Partial<KnowledgeItem> & { id: string }

export function createSettings(detail?: ApplicationDetail): ApplicationSettings {
  const defaults: ApplicationSettings = {
    name: '',
    desc: '',
    model_id: '',
    dialogue_number: 1,
    prologue: '您好，我是 MaxKB 智能客服，您可以向我提出 MaxKB 使用问题。',
    model_setting: {
      system: '',
      prompt: '已知信息：\n{data}\n请根据已知信息回答用户的问题。\n问题：{question}',
      no_references_prompt: '{question}',
      reasoning_content_enable: false,
      reasoning_content_start: '<think>',
      reasoning_content_end: '</think>',
    },
    knowledge_setting: {
      search_mode: 'embedding',
      top_n: 3,
      similarity: 0.6,
      max_paragraph_char_number: 5000,
      no_references_setting: { status: 'ai_questioning', value: '{question}' },
    },
    knowledge_id_list: [],
    application_ids: [],
    tool_ids: [],
    skill_tool_ids: [],
    mcp_tool_ids: [],
    model_params_setting: {},
    stt_model_id: '',
    stt_model_params_setting: {},
    tts_model_id: '',
    tts_model_params_setting: {},
    stt_model_enable: false,
    tts_model_enable: false,
    tts_type: 'BROWSER',
    stt_autosend: false,
    tts_autoplay: false,
    long_term_enable: false,
    long_term_model_id: '',
    long_term_model_params_setting: {},
    long_term_trigger_type: 'ROUND',
    long_term_trigger_setting: { rounds: 10 },
    application_enable: true,
    tool_enable: true,
    mcp_enable: true,
    mcp_source: 'referencing',
    mcp_servers: '',
    mcp_output_enable: false,
    problem_optimization: false,
    problem_optimization_prompt: DEFAULT_PROBLEM_OPTIMIZATION_PROMPT,
  }
  if (!detail) return defaults
  // 保留详情中的扩展配置，只为已有字段补充缺省值；模型响应字段使用 v2 的别名。
  return {
    ...defaults,
    ...cloneDeep(detail),
    name: detail.name,
    desc: detail.desc ?? '',
    problem_optimization_prompt: detail.problem_optimization_prompt || DEFAULT_PROBLEM_OPTIMIZATION_PROMPT,
    mcp_source: detail.mcp_source === 'custom' ? 'custom' : 'referencing',
    mcp_servers: detail.mcp_servers ?? '',
    mcp_output_enable: detail.mcp_output_enable ?? false,
    model_id: detail.model ?? detail.model_id ?? '',
    stt_model_id: detail.stt_model ?? detail.stt_model_id ?? '',
    tts_model_id: detail.tts_model ?? detail.tts_model_id ?? '',
    long_term_model_id: detail.long_term_model ?? detail.long_term_model_id ?? '',
    long_term_trigger_type: detail.long_term_trigger_type === 'SCHEDULED' ? 'SCHEDULED' : 'ROUND',
    model_setting: { ...defaults.model_setting, ...cloneDeep(detail.model_setting) },
    knowledge_setting: {
      ...defaults.knowledge_setting,
      ...cloneDeep(detail.knowledge_setting),
      no_references_setting: {
        ...defaults.knowledge_setting.no_references_setting,
        ...cloneDeep(detail.knowledge_setting?.no_references_setting as KnowledgeSetting['no_references_setting'] | undefined),
      },
    },
  }
}

/** 详情中的画布和只读字段不参与简易配置保存；空 UUID 按后端协议提交 null。 */
export function createSettingsPayload(settings: ApplicationSettings): ApplicationFormPayload {
  const payload: ApplicationFormPayload = cloneDeep(settings)
  const responseFields = [
    'id',
    'model',
    'stt_model',
    'tts_model',
    'long_term_model',
    'knowledge_list',
    'application_list',
    'tool_list',
    'skill_tool_list',
    'work_flow',
    'create_time',
    'update_time',
    'publish_time',
    'is_publish',
    'resource_type',
    'resource_count',
    'user_id',
    'folder',
  ]
  for (const field of responseFields) delete (payload as Record<string, unknown>)[field]
  payload.stt_model_id = settings.stt_model_id || null
  payload.tts_model_id = settings.tts_model_id || null
  payload.long_term_model_id = settings.long_term_model_id || null
  return payload
}
