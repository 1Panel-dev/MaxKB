import {Result} from '@/request/Result.ts'
import {get, post} from '@/request'
import type {LoginRequest} from '@/api/type/login.ts'
import type {Ref} from 'vue'

/**
 * 登录
 * @param request 登录接口请求表单
 * @param loading 接口加载器
 * @returns 认证数据
 */
const login: (accessToken: string, request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  accessToken: string,
  request,
  loading,
) => {
  return post('/chat_user/login/' + accessToken, request, undefined, loading)
}

const ldapLogin: (accessToken: string, request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  accessToken: string,
  request,
  loading,
) => {
  return post('/chat_user/ldap/login/' + accessToken, request, undefined, loading)
}


/**
 * 获取验证码
 * @param loading 接口加载器
 */
const getCaptcha: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/user/captcha', undefined, loading)
}

/**
 * 获取登录方式
 */
const getAuthType: (accessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (accessToken, loading) => {
  return get('chat_user/auth/types/' + accessToken, undefined, loading)
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
  loading
) => {
  return get('dingtalk', {code}, loading)
}

const getDingOauth2Callback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading
) => {
  return get('dingtalk/oauth2', {code}, loading)
}

const getWecomCallback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading
) => {
  return get('wecom', {code}, loading)
}
const getLarkCallback: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading
) => {
  return get('lark/oauth2', {code}, loading)
}


export default {
  login,
  getCaptcha,
  getAuthType,
  getDingCallback,
  getQrType,
  getWecomCallback,
  getDingOauth2Callback,
  getLarkCallback,
  getQrSource,
  ldapLogin
}
