import { Result } from '@/request/Result'
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
import { type ChatProfile } from '@/api/type/chat'
import { type Ref } from 'vue'

import useStore from '@/stores'
import type { LoginRequest } from '@/api/type/user'

const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
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
  return postStream(`/chat/api/chat_message/${chat_id}`, data)
}
const chatProfile: (assessToken: string, loading?: Ref<boolean>) => Promise<Result<ChatProfile>> = (
  assessToken,
  loading,
) => {
  return get('/profile', { access_token: assessToken }, loading)
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
  return post('/auth/anonymous', { access_token: assessToken }, {}, loading)
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
 * @param loading 接口加载器
 */
const getCaptcha: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/captcha', undefined, loading)
}

/**
 * 获取二维码类型
 */
const getQrType: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('qr_type', undefined, loading)
}

const getQrSource: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('qr_type/source', undefined, loading)
}

const getDingCallback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return get('dingtalk', { code }, loading)
}

const getDingOauth2Callback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return get('dingtalk/oauth2', { code }, loading)
}

const getWecomCallback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return get('wecom', { code }, loading)
}
const getLarkCallback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return get('lark/oauth2', { code }, loading)
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
}
