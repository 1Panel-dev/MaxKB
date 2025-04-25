import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { LoginRequest } from '@/api/type/login'
import type { Ref } from 'vue'

/**
 * 登录
 * @param request 登录接口请求表单
 * @param loading 接口加载器
 * @returns 认证数据
 */
const login: (request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
  request,
  loading,
) => {
  return post('/user/login', request, undefined, loading)
}

/**
 * 获取验证码
 * @param loading 接口加载器
 */
const getCaptcha: (loading?: Ref<boolean>) => Promise<Result<string>> = (loading) => {
  return get('/user/captcha', undefined, loading)
}

export default {
  login,
  getCaptcha,
}
