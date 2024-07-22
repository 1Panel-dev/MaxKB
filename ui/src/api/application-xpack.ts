import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/application'

/**
 * 替换社区版-获取AccessToken
 * @param 参数 application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading
) => {
  return get(`${prefix}/${application_id}/setting`, undefined, loading)
}

/**
 * 替换社区版-修改AccessToken
 * @param 参数 application_id
 * data {
 *  "show_source": boolean,
 *  "show_history": boolean,
 *  "draggable": boolean,
 *  "show_guide": boolean,
 *  "avatar": file,
 *  "float_icon": file,
 * }
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/setting`, data, undefined, loading)
}

/**
 * 对话获取应用相关信息
 * @param 参数 
 {
  "access_token": "string"
}
 */
const getAppXpackProfile: (loading?: Ref<boolean>) => Promise<any> = (loading) => {
  return get(`${prefix}/xpack/profile`, undefined, loading)
}

export default {
  getAccessToken,
  putAccessToken,
  getAppXpackProfile
}
