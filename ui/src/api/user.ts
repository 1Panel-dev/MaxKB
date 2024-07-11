import {Result} from '@/request/Result'
import {get, post} from '@/request/index'
import type {
    LoginRequest,
    RegisterRequest,
    CheckCodeRequest,
    ResetPasswordRequest,
    User,
    ResetCurrentUserPasswordRequest
} from '@/api/type/user'
import type {Ref} from 'vue'

/**
 * 登录
 * @param auth_type
 * @param request 登录接口请求表单
 * @param loading 接口加载器
 * @returns 认证数据
 */
const login: (auth_type: string, request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
    auth_type,
    request,
    loading
) => {
    if (auth_type !== '') {
        return post(`/${auth_type}/login`, request, undefined, loading)
    }
    return post('/user/login', request, undefined, loading)
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
 * 注册用户
 * @param request 注册请求对象
 * @param loading 接口加载器
 * @returns
 */
const register: (request: RegisterRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
    request,
    loading
) => {
    return post('/user/register', request, undefined, loading)
}

/**
 * 校验验证码
 * @param request 请求对象
 * @param loading 接口加载器
 * @returns
 */
const checkCode: (request: CheckCodeRequest, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
    request,
    loading
) => {
    return post('/user/check_code', request, undefined, loading)
}

/**
 * 发送邮件
 * @param email  邮件地址
 * @param loading 接口加载器
 * @returns
 */
const sendEmit: (
    email: string,
    type: 'register' | 'reset_password',
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (email, type, loading) => {
    return post('/user/send_email', {email, type}, undefined, loading)
}
/**
 * 发送邮件到当前用户
 * @param loading  发送验证码到当前用户
 * @returns
 */
const sendEmailToCurrent: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
    return post('/user/current/send_email', undefined, undefined, loading)
}
/**
 * 修改当前用户密码
 * @param request 请求对象
 * @param loading 加载器
 * @returns
 */
const resetCurrentUserPassword: (
    request: ResetCurrentUserPasswordRequest,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
    return post('/user/current/reset_password', request, undefined, loading)
}
/**
 * 获取用户基本信息
 * @param loading 接口加载器
 * @returns 用户基本信息
 */
const profile: (loading?: Ref<boolean>) => Promise<Result<User>> = (loading) => {
    return get('/user', undefined, loading)
}

/**
 * 重置密码
 * @param request 重置密码请求参数
 * @param loading 接口加载器
 * @returns
 */
const resetPassword: (
    request: ResetPasswordRequest,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
    return post('/user/re_password', request, undefined, loading)
}

/**
 * 添加团队需要查询用户列表
 * @param loading 接口加载器
 * email_or_username
 */
const getUserList: (email_or_username: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
    email_or_username,
    loading
) => {
    return get('/user/list', {email_or_username}, loading)
}

/**
 * 获取profile
 */
const getProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
    return get('/profile', undefined, loading)
}

/**
 * 获取校验
 * @param valid_type 校验类型: application|dataset|user
 * @param valid_count 校验数量: 5 | 50 | 2
 */
const getValid: (
    valid_type: string,
    valid_count: number,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (valid_type, valid_count, loading) => {
    return get(`/valid/${valid_type}/${valid_count}`, undefined, loading)
}
/**
 * 获取登录方式
 */
const getAuthType: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
    return get('auth/types', undefined, loading)
}

export default {
    login,
    register,
    sendEmit,
    checkCode,
    profile,
    resetPassword,
    sendEmailToCurrent,
    resetCurrentUserPassword,
    logout,
    getUserList,
    getProfile,
    getValid,
    getAuthType
}
