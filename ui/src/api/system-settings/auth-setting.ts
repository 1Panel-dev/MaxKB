import {Result} from '@/request/Result'
import {get, post, put} from '@/request/index'
import {type Ref} from 'vue'

const prefix = '/auth'
/**
 * 获取认证设置
 */
const getAuthSetting: (auth_type: string, loading?: Ref<boolean>) => Promise<Result<any>> = (auth_type, loading) => {
  return get(`${prefix}/${auth_type}/detail`, undefined, loading)
}

/**
 * ldap连接测试
 */
const postAuthSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/connection`, data, undefined, loading)
}

/**
 * 修改邮箱设置
 */
const putAuthSetting: (auth_type: string, data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  auth_type,
  data,
  loading
) => {
  return put(`${prefix}/${auth_type}/info`, data, undefined, loading)
}
/**
 * 登录设置
 */
const putLoginSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return put(`${prefix}/setting`, data, undefined, loading)
}
/**
 * 获取登录设置
 */
const getLoginSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}/setting`, undefined, loading)
}

const getLoginAuthSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`login/auth/setting`, undefined, loading)
}

/**
 * 获取认证设置
 */
const getLoginViewAuthSetting: (auth_type: string, loading?: Ref<boolean>) => Promise<Result<any>> = (auth_type, loading) => {
  return get(`login${prefix}/${auth_type}/detail`, undefined, loading)
}

export default {
  getAuthSetting,
  postAuthSetting,
  putAuthSetting,
  putLoginSetting,
  getLoginSetting,
  getLoginAuthSetting,
  getLoginViewAuthSetting
}
