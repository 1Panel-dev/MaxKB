import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { User, ResetPasswordRequest, CheckCodeRequest } from '@/api/type/user'
import type { Ref } from 'vue'
import type { KeyValue, pageRequest } from '@/api/type/common'
import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/trigger'
  },
})
/**
 * 分页查询触发器
 * @param page    分页参数
 * @param param   查询参数
 * @param loading 加载器
 * @returns
 */
const pageTrigger = (page: pageRequest, param: any, loading?: Ref<boolean>) => {
  return get(`${prefix.value}/${page.current_page}/${page.page_size}`, param, loading)
}
export default { pageTrigger }
