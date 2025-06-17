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

const prefix = '/workspace/' + localStorage.getItem('workspace_id') + '/application'

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
export default {
  open,
  chat,
  chatProfile,
  anonymousAuthentication,
  applicationProfile,
}
