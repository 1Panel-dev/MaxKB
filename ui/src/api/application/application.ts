import { Result } from '@/request/Result'
import { get, post, postStream, del, put, request, download, exportFile } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'
import useStore from '@/stores'

const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/application'
  },
})
/**
 * 获取全部应用
 * @param param
 * @param loading
 */
const getAllApplication: (param?: any, loading?: Ref<boolean>) => Promise<Result<any[]>> = (
  param,
  loading,
) => {
  return get(`${prefix.value}`, param, loading)
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
  return get(`${prefix.value}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建应用
 * @param data
 * @param loading
 */
const postApplication: (
  data: ApplicationFormType,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix.value}`, data, undefined, loading)
}

/**
 * 修改应用
 * @param application_id
 * @param data
 * @param loading
 */
const putApplication: (
  application_id: string,
  data: ApplicationFormType,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix.value}/${application_id}`, data, undefined, loading)
}

/**
 * 删除应用
 * @param application_id
 * @param loading
 */
const delApplication: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (application_id, loading) => {
  return del(`${prefix.value}/${application_id}`, undefined, {}, loading)
}

/**
 * 应用详情
 * @param application_id
 * @param loading
 */
const getApplicationDetail: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix.value}/${application_id}`, undefined, loading)
}

/**
 * 获取AccessToken
 * @param application_id
 * @param loading
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading,
) => {
  return get(`${prefix.value}/${application_id}/access_token`, undefined, loading)
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
  return get(`${prefix.value}/${application_id}/setting`, undefined, loading)
}

/**
 * 修改AccessToken
 * data {
 *  "is_active": true
 * }
 * @param application_id
 * @param data
 * @param loading
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix.value}/${application_id}/access_token`, data, undefined, loading)
}

/**
 * 替换社区版-修改AccessToken
 * data {
 *  "show_source": boolean,
 *  "show_history": boolean,
 *  "draggable": boolean,
 *  "show_guide": boolean,
 *  "avatar": file,
 *  "float_icon": file,
 * }
 * @param application_id
 * @param data
 * @param loading
 */
const putXpackAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix.value}/${application_id}/setting`, data, undefined, loading)
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
    `${prefix.value}/${application_id}/export`,
    undefined,
    loading,
  )
}

/**
 * 导入应用
 */
const importApplication: (
  folder_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (folder_id, data, loading) => {
  return post(`${prefix.value}/folder/${folder_id}/import`, data, undefined, loading)
}

/**
 * 统计
 * @param application_id
 * @param data
 * @param loading
 */
const getStatistics: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix.value}/${application_id}/application_stats`, data, loading)
}
/**
 * 统计token消耗
 */
const getTokenUsage: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix.value}/${application_id}/application_token_usage`, data, loading)
}
/**
 * 统计提问次数
 */
const topQuestions: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix.value}/${application_id}/top_questions`, data, loading)
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
  return get(`${prefix.value}/${application_id}/open`, {}, loading)
}

/**
 * 生成提示词
 * @param workspace_id
 * @param model_id
 * @param application_id
 * @param data
 * @returns
 */
const generate_prompt: (workspace_id:string ,model_id:string, application_id:string,data: any) => Promise<any> = (
  workspace_id,
  model_id,
  application_id,
  data
) => {
  const prefix = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  return postStream(`${prefix}/workspace/${workspace_id}/application/${application_id}/model/${model_id}/prompt_generate`, data)
}


/**
 * 对话
 * chat_id: string
 * data
 * @param chat_id
 * @param data
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
  return get(`${prefix.value}/${application_id}/platform/status`)
}
/**
 * 更新平台状态
 */
const updatePlatformStatus: (application_id: string, data: any) => Promise<Result<any>> = (
  application_id,
  data,
) => {
  return post(`${prefix.value}/${application_id}/platform/status`, data)
}
/**
 * 获取平台配置
 */
const getPlatformConfig: (application_id: string, type: string) => Promise<Result<any>> = (
  application_id,
  type,
) => {
  return get(`${prefix.value}/${application_id}/platform/${type}`)
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
  return post(`${prefix.value}/${application_id}/platform/${type}`, data, undefined, loading)
}
/**
 * 应用发布
 * @param application_id
 * @param data
 * @param loading
 * @returns
 */
const publish: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix.value}/${application_id}/publish`, data, {}, loading)
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
  return download(
    `${prefix.value}/${application_id}/play_demo_text`,
    'post',
    data,
    undefined,
    loading,
  )
}

/**
 * 文本转语音
 */
const postTextToSpeech: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return download(
    `${prefix.value}/${application_id}/text_to_speech`,
    'post',
    data,
    undefined,
    loading,
  )
}
/**
 * 语音转文本
 */
const speechToText: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return post(`${prefix.value}/${application_id}/speech_to_text`, data, undefined, loading)
}

/**
 * mcp 节点
 */
const getMcpTools: (
  application_id: string,
  mcp_servers: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, mcp_servers, loading) => {
  return post(`${prefix.value}/${application_id}/mcp_tools`, { mcp_servers }, {}, loading)
}

/**
 * 上传文件
 * @param file
 * @param sourceId
 * @param resourceType
 * @param loading
 */
const postUploadFile: (
  file: any,
  sourceId: string,
  resourceType:
    | 'KNOWLEDGE'
    | 'APPLICATION'
    | 'TOOL'
    | 'DOCUMENT'
    | 'CHAT'
    | 'TEMPORARY_30_MINUTE'
    | 'TEMPORARY_120_MINUTE'
    | 'TEMPORARY_1_DAY',
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (file, sourceId, resourceType, loading) => {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('source_id', sourceId)
  fd.append('source_type', resourceType)
  return post(`/oss/file`, fd, undefined, loading)
}

export default {
  getAllApplication,
  getApplication,
  postApplication,
  putApplication,
  delApplication,
  getApplicationDetail,
  getAccessToken,
  putAccessToken,
  putXpackAccessToken,
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
  postUploadFile,
  generate_prompt,
  getTokenUsage,
  topQuestions
}
