import { Result } from '@/request/Result'
import { get, post, postStream, del, put, request, download, exportFile } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'

const prefix = '/system/resource/application'

/**
 * 获取全部应用
 * @param param
 * @param loading
 */
const getAllApplication: (param?: any, loading?: Ref<boolean>) => Promise<Result<any[]>> = (
  param,
  loading,
) => {
  return get(`${prefix}`, param, loading)
}
/**
 * 获取分页应用
 * param {
 "name": "string",
 }
 */
const getApplication: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 修改应用
 * @param 参数
 */
const putApplication: (
  application_id: string,
  data: ApplicationFormType,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}`, data, undefined, loading)
}

/**
 * 删除应用
 * @param 参数 application_id
 */
const delApplication: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (application_id, loading) => {
  return del(`${prefix}/${application_id}`, undefined, {}, loading)
}

/**
 * 应用详情
 * @param 参数 application_id
 */
const getApplicationDetail: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}`, undefined, loading)
}

/**
 * 获取AccessToken
 * @param 参数 application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading,
) => {
  return get(`${prefix}/${application_id}/access_token`, undefined, loading)
}
/**
 * 修改AccessToken
 * @param 参数 application_id
 * data {
 *  "is_active": true
 * }
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/access_token`, data, undefined, loading)
}

/**
 * 替换社区版-修改AccessToken
 * @param 参数 application_id
 * data {
 *  "show_source": boolean,
 *  "show_history": boolean,
 *  "draggable": boolean,
 *  "show_guide": boolean,
 *  "avatar": file,
 *  "float_icon": file,
 * }
 */
const putXpackAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/setting`, data, undefined, loading)
}

/**
 * 统计
 * @param 参数 application_id, data
 */
const getStatistics: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/application_stats`, data, loading)
}
/**
 * 统计token消耗
 */
const getTokenUsage: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/application_token_usage`, data, loading)
}
const topQuestions: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/top_questions`, data, loading)
}
/**
 * 打开调试对话id
 * @param application_id 应用id
 * @param loading 加载器
 * @returns
 */
const open: (application_id: string, loading?: Ref<boolean>) => Promise<Result<string>> = (
  application_id,
  loading,
) => {
  return get(`${prefix}/${application_id}/open`, {}, loading)
}

/**
 * 生成提示词
 * @param application_id
 * @param model_id
 * @param data
 * @returns
 */
const generate_prompt: (application_id:string, model_id:string, data: any) => Promise<any> = (
  application_id,
  model_id,
  data
) => {
  const prefix = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  return postStream(`${prefix}/system/resource/application/${application_id}/model/${model_id}/prompt_generate`, data)
}


/**
 * 应用发布
 * @param application_id
 * @param loading
 * @returns
 */
const publish: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/publish`, data, {}, loading)
}

/**
 *
 * @param application_id
 * @param data
 * @param loading
 * @returns
 */
const playDemoText: (application_id: string, data: any, loading?: Ref<boolean>) => Promise<any> = (
  application_id,
  data,
  loading,
) => {
  return download(`${prefix}/${application_id}/play_demo_text`, 'post', data, undefined, loading)
}

/**
 * 文本转语音
 */
const postTextToSpeech: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return download(`${prefix}/${application_id}/text_to_speech`, 'post', data, undefined, loading)
}
/**
 * 语音转文本
 */
const speechToText: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return post(`${prefix}/${application_id}/speech_to_text`, data, undefined, loading)
}

/**
 * 获取应用设置
 * @param application_id 应用id
 * @param loading 加载器
 * @returns
 */
const getApplicationSetting: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/setting`, undefined, loading)
}

/**
 * 导出应用
 */

const exportApplication = (
  application_id: string,
  application_name: string,
  loading?: Ref<boolean>,
) => {
  return exportFile(
    application_name + '.mk',
    `${prefix}/${application_id}/export`,
    undefined,
    loading,
  )
}

/**
 * 导入应用
 */
const importApplication: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/import`, data, undefined, loading)
}

/**
 * 对话
 * @param 参数
 * chat_id: string
 * data
 */
const chat: (chat_id: string, data: any) => Promise<any> = (chat_id, data) => {
  const prefix = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  return postStream(`${prefix}/chat_message/${chat_id}`, data)
}
/**
 * 获取对话用户认证类型
 * @param loading 加载器
 * @returns
 */
const getChatUserAuthType: (loading?: Ref<boolean>) => Promise<any> = (loading) => {
  return get(`/chat_user/auth/types`, {}, loading)
}

/**
 * 获取平台状态
 */
const getPlatformStatus: (application_id: string) => Promise<Result<any>> = (application_id) => {
  return get(`${prefix}/${application_id}/platform/status`)
}
/**
 * 更新平台状态
 */
const updatePlatformStatus: (application_id: string, data: any) => Promise<Result<any>> = (
  application_id,
  data,
) => {
  return post(`${prefix}/${application_id}/platform/status`, data)
}
/**
 * 获取平台配置
 */
const getPlatformConfig: (application_id: string, type: string) => Promise<Result<any>> = (
  application_id,
  type,
) => {
  return get(`${prefix}/${application_id}/platform/${type}`)
}
/**
 * 更新平台配置
 */
const updatePlatformConfig: (
  application_id: string,
  type: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, type, data, loading) => {
  return post(`${prefix}/${application_id}/platform/${type}`, data, undefined, loading)
}

/**
 * mcp 节点
 */
const getMcpTools: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading,
) => {
  return get(`${prefix}/${application_id}/mcp_tools`, undefined, loading)
}

export default {
  getAllApplication,
  getApplication,
  putApplication,
  delApplication,
  getApplicationDetail,
  getAccessToken,
  putAccessToken,
  exportApplication,
  importApplication,
  getStatistics,
  open,
  chat,
  getChatUserAuthType,
  getApplicationSetting,
  getPlatformStatus,
  updatePlatformStatus,
  getPlatformConfig,
  publish,
  updatePlatformConfig,
  playDemoText,
  postTextToSpeech,
  speechToText,
  getMcpTools,
  putXpackAccessToken,
  generate_prompt,
  getTokenUsage,
  topQuestions
}
