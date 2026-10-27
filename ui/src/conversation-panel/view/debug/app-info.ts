/** debug 模式的智能体信息：由 Admin 智能体详情与显示设置转为对话端 profile 结构。 */

import { cloneDeep } from 'lodash'
import type { ApplicationDetail, ApplicationDisplaySetting, Dict } from '@/api/types'
import { APPLICATION_DISPLAY_SETTING_DEFAULT } from '@/constants/application'
import type { ConversationAppInfo } from '../../core/types'

const BASE_NODE_ID = 'base-node'

/** 显示设置补齐默认值：接口未返回的字段（社区版没有显示设置接口）使用默认值，嵌套配置分别合并。 */
function resolveDisplaySetting(config?: Partial<ApplicationDisplaySetting> | null): ApplicationDisplaySetting {
  const defaults = APPLICATION_DISPLAY_SETTING_DEFAULT
  const setting: ApplicationDisplaySetting = cloneDeep(defaults)
  for (const key of Object.keys(setting) as (keyof ApplicationDisplaySetting)[]) {
    if (config?.[key] != null) Object.assign(setting, { [key]: cloneDeep(config[key]) })
  }
  setting.custom_theme = { ...defaults.custom_theme, ...config?.custom_theme }
  setting.float_location = {
    x: { ...defaults.float_location.x, ...config?.float_location?.x },
    y: { ...defaults.float_location.y, ...config?.float_location?.y },
  }
  return setting
}

/**
 * 把 Admin 智能体详情转为与对话端 profile 相同的结构，下游组件不区分 chat / debug。
 * 工作流保存时开始节点的名称、语音、文件上传配置已同步到应用字段；开场白与描述要到发布才同步，需从开始节点读取草稿。
 * displayConfig 为专业版、企业版的显示设置，社区版不传；缺失的字段补齐默认值。
 * 访问设置按调试场景固定，不读取接口：始终显示知识来源与执行详情（与 v2 一致），调试面板没有分享。
 */
export function toDebugAppInfo(detail: ApplicationDetail, displayConfig?: Partial<ApplicationDisplaySetting> | null): ConversationAppInfo {
  const baseNode = detail.work_flow?.nodes?.find((node) => node.id === BASE_NODE_ID)
  const nodeData = (baseNode?.properties?.node_data ?? {}) as Dict<unknown>
  const readNodeText = (key: string, fallback?: string | null) => (typeof nodeData[key] === 'string' ? (nodeData[key] as string) : fallback)
  const display = resolveDisplaySetting(displayConfig)

  return {
    id: detail.id,
    name: detail.name,
    icon: detail.icon ?? '',
    desc: readNodeText('desc', detail.desc),
    prologue: readNodeText('prologue', detail.prologue) ?? '',
    type: detail.type,
    dialogue_number: detail.dialogue_number,
    problem_optimization: detail.problem_optimization,
    stt_model_id: detail.stt_model_id,
    tts_model_id: detail.tts_model_id,
    stt_model_enable: detail.stt_model_enable,
    tts_model_enable: detail.tts_model_enable,
    tts_type: detail.tts_type,
    tts_autoplay: detail.tts_autoplay,
    stt_autosend: detail.stt_autosend,
    file_upload_enable: detail.file_upload_enable,
    file_upload_setting: detail.file_upload_setting,
    work_flow: baseNode ? { nodes: [baseNode] } : null,
    show_source: true,
    show_exec: true,
    show_share: false,
    language: display.language || null,
    show_history: display.show_history,
    draggable: display.draggable,
    avatar: display.avatar,
    show_avatar: display.show_avatar,
    float_icon: display.float_icon,
    disclaimer: display.disclaimer,
    disclaimer_value: display.disclaimer_value,
    custom_theme: display.custom_theme,
    user_avatar: display.user_avatar,
    show_user_avatar: display.show_user_avatar,
    float_location: display.float_location,
    chat_background: display.chat_background,
  }
}
