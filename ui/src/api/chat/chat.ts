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
 * 对话
 * @param 参数
 * chat_id: string
 * data
 */
const chat: (chat_id: string, data: any) => Promise<any> = (chat_id, data) => {
  return postStream(`/api/chat_message/${chat_id}`, data)
}
const chatProfile: (assessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  assessToken,
  loading,
) => {
  return get('/auth/profile', { access_token: assessToken }, loading)
}
const applicationProfile: (assessToken: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  assessToken,
  loading,
) => {
  return get('/chat/api/profile')
}
export default {
  open,
  chat,
  chatProfile,
}
