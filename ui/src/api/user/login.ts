import {Result} from '@/request/Result'
import {get, post} from '@/request/index'
import type {LoginRequest} from '@/api/type/login'
import type {Ref} from 'vue'
import type {User} from "@/api/type/user.ts";

/**
 * 登录
 * @param request 登录接口请求表单
 * @param loading 接口加载器
 * @returns 认证数据
 */
const login: (request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  request,
  loading,
) => {
  return post('/user/login', request, undefined, loading)
}

const ldapLogin: (request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  request,
  loading,
) => {
  return post('/ldap/login', request, undefined, loading)
}


/**
 * 登出
 * @param loading 接口加载器
 * @returns
 */
const logout: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/user/logout', undefined, undefined, loading)
}

/**
 * 获取验证码
 * @param loading 接口加载器
 */
const getCaptcha: (username?: string, loading?: Ref<boolean>) => Promise<Result<any>> = (username, loading) => {
  return get('/user/captcha', {username}, loading)
}

/**
 * 获取登录方式
 */
const getAuthType: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('auth/types', undefined, loading)
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

/**
 * 设置语言
 * data: {
 * "language": "string"
 * }
 */
const postLanguage: (data: any, loading?: Ref<boolean>) => Promise<Result<User>> = (
  data,
  loading
) => {
  return post('/user/language', data, undefined, loading)
}
const samlLogin: (loading?: Ref<boolean>) => Promise<Result<any>> = (
  loading,
) => {
  return get('/saml2', '', loading)
}
export default {
  login,
  logout,
  getCaptcha,
  getAuthType,
  getDingCallback,
  getQrType,
  getWecomCallback,
  postLanguage,
  getDingOauth2Callback,
  getLarkCallback,
  getQrSource,
  ldapLogin,
  samlLogin
}
