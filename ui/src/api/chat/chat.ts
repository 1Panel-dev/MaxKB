import {Result} from '@/request/Result'
import {
  get,
  post,
  postStream,
  del,
  put,
  request,
  download,
  exportFile,
} from '@/request/chat/index'
import {type ChatProfile} from '@/api/type/chat'
import {type Ref} from 'vue'
import type {ResetPasswordRequest} from '@/api/type/user.ts'

import useStore from '@/stores'
import type {LoginRequest} from '@/api/type/user'

const prefix: any = {_value: '/workspace/'}
Object.defineProperty(prefix, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId() + '/application'
  },
})

/**
 * 打开调试对话id
 * @param application_id 应用id
 * @param loading 加载器
 * @returns
 */
const open: (loading?: Ref<boolean>) => Promise<Result<string>> = (loading) => {
  return get('/open', {}, loading)
}
/**
 * 对话
 * @param 参数
 * chat_id: string
 * data
 */
const chat: (chat_id: string, data: any) => Promise<any> = (chat_id, data) => {
  const prefix = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/chat') + '/api'
  return postStream(`${prefix}/chat_message/${chat_id}`, data)
}

/**
 * 应用认证信息
 */
const chatProfile: (assessToken: string, loading?: Ref<boolean>) => Promise<Result<ChatProfile>> = (
  assessToken,
  loading,
) => {
  return get('/profile', {access_token: assessToken}, loading)
}
/**
 * 匿名认证
 * @param assessToken
 * @param loading
 * @returns
 */
const anonymousAuthentication: (
  assessToken: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (assessToken, loading) => {
  return post('/auth/anonymous', {access_token: assessToken}, {}, loading)
}
/**
 * 密码认证
 * @param assessToken
 * @param password
 * @param loading
 * @returns
 */
const passwordAuthentication: (
  assessToken: string,
  password: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (assessToken, password, loading) => {
  return post('auth/password', {access_token: assessToken, password: password}, {}, loading)
}
/**
 * 获取应用相关信息
 * @param loading
 * @returns
 */
const applicationProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/application/profile', {}, loading)
}

/**
 * 登录
 * @param request 登录接口请求表单
 * @param loading 接口加载器
 * @returns 认证数据
 */
const login: (
  accessToken: string,
  request: LoginRequest,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (accessToken: string, request, loading) => {
  return post('/auth/login/' + accessToken, request, undefined, loading)
}

const ldapLogin: (
  accessToken: string,
  request: LoginRequest,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (accessToken: string, request, loading) => {
  return post('/auth/ldap/login/' + accessToken, request, undefined, loading)
}

/**
 * 获取验证码
 * @param username
 * @param loading 接口加载器
 */
const getCaptcha: (username?: string, accessToken?: string, loading?: Ref<boolean>) => Promise<Result<any>> = (username, accessToken, loading) => {
  return get('/captcha', {username: username, accessToken: accessToken}, loading)
}

/**
 * 获取二维码类型
 */
const getQrType: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('auth/qr_type', undefined, loading)
}

const getQrSource: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('auth/qr_type/source', undefined, loading)
}

const getDingCallback: (code: string, accessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  accessToken,
  loading,
) => {
  return get('auth/dingtalk', {code, accessToken: accessToken}, loading)
}

const getDingOauth2Callback: (code: string, accessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  accessToken,
  loading,
) => {
  return get('auth/dingtalk/oauth2', {code, accessToken: accessToken}, loading)
}

const getWecomCallback: (code: string, accessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  accessToken,
  loading,
) => {
  return get('auth/wecom', {code, accessToken: accessToken}, loading)
}
const getLarkCallback: (code: string, accessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  accessToken,
  loading,
) => {
  return get('auth/lark/oauth2', {code, accessToken: accessToken}, loading)
}

/**
 * 获取认证设置
 */
const getAuthSetting: (auth_type: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  auth_type,
  loading,
) => {
  return get(`/chat_user/${auth_type}/detail`, undefined, loading)
}
/**
 * 点赞点踩
 * @param chat_id         对话id
 * @param chat_record_id  对话记录id
 * @param vote_status     点赞状态
 * @param loading         加载器
 * @returns
 */
const vote: (
  chat_id: string,
  chat_record_id: string,
  vote_status: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (chat_id, chat_record_id, vote_status, loading) => {
  return put(
    `/vote/chat/${chat_id}/chat_record/${chat_record_id}`,
    {
      vote_status,
    },
    undefined,
    loading,
  )
}
const pageChat: (
  current_page: number,
  page_size: number,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (current_page, page_size, loading) => {
  return get(`/historical_conversation/${current_page}/${page_size}`, undefined, loading)
}
const pageChatRecord: (
  chat_id: string,
  current_page: number,
  page_size: number,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (chat_id, current_page, page_size, loading) => {
  return get(
    `/historical_conversation_record/${chat_id}/${current_page}/${page_size}`,
    undefined,
    loading,
  )
}

/**
 * 登出
 */
const logout: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/auth/logout', undefined, undefined, loading)
}

/**
 * 重置密码
 */
const resetCurrentPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/chat_user/current/reset_password', request, undefined, loading)
}

/**
 * 获取当前用户信息
 */
const getChatUserProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/chat_user/profile', {}, loading)
}
/**
 * 获取对话详情
 * @param chat_id         对话id
 * @param chat_record_id  对话记录id
 * @param loading         加载器
 * @returns
 */
const getChatRecord: (
  chat_id: string,
  chat_record_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (chat_id, chat_record_id, loading) => {
  return get(`historical_conversation/${chat_id}/record/${chat_record_id}`, {}, loading)
}
/**
 * 文本转语音
 */
const textToSpeech: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return download(`text_to_speech`, 'post', data, undefined, loading)
}

/**
 * 语音转文本
 */
const speechToText: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`speech_to_text`, data, undefined, loading)
}
/**
 *
 * @param chat_id  对话ID
 * @param loading
 * @returns
 */
const deleteChat: (chat_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  chat_id,
  loading,
) => {
  return del(`historical_conversation/${chat_id}`, undefined, undefined, loading)
}
/**
 *
 * @param loading
 * @returns
 */
const clearChat: (loading?: Ref<boolean>) => Promise<Result<any>> = (
  loading
) => {
  return del(`historical_conversation/clear`, undefined, undefined, loading)
}
/**
 *
 * @param chat_id 对话id
 * @param data    对话简介
 * @param loading
 * @returns
 */
const modifyChat: (chat_id: string, data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  chat_id,
  data,
  loading,
) => {
  return put(`historical_conversation/${chat_id}`, data, undefined, loading)
}
/**
 * 上传文件
 * @param file      文件
 * @param sourceId  资源id
 * @param resourceType  资源类型
 * @returns
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
) => Promise<Result<any>> = (file, sourceId, sourceType, loading) => {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('source_id', sourceId)
  fd.append('source_type', sourceType)
  return post(`/oss/file`, fd, undefined, loading)
}
export default {
  open,
  chat,
  chatProfile,
  anonymousAuthentication,
  applicationProfile,
  login,
  getCaptcha,
  getDingCallback,
  getQrType,
  getWecomCallback,
  getDingOauth2Callback,
  getLarkCallback,
  getQrSource,
  ldapLogin,
  getAuthSetting,
  passwordAuthentication,
  vote,
  pageChat,
  pageChatRecord,
  logout,
  resetCurrentPassword,
  getChatUserProfile,
  getChatRecord,
  textToSpeech,
  speechToText,
  deleteChat,
  clearChat,
  modifyChat,
  postUploadFile,
}
