import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import useStore from '@/stores'
import { type Ref } from 'vue'

const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/application'
  },
})

/**
 * 替换社区版-获取AccessToken
 * @param 参数 application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading,
) => {
  return get(`${prefix.value}/${application_id}/setting`, undefined, loading)
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
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix.value}/${application_id}/setting`, data, undefined, loading)
}

export default {
  getAccessToken,
  putAccessToken,
}
