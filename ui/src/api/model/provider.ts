import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { Ref } from 'vue'
const trigger: (
  provider: string,
  method: string,
  request_body: any,
  loading?: Ref<boolean>
) => Promise<Result<Array<any> | string>> = (provider, method, request_body, loading) => {
  return post(`provider/${provider}/${method}`, {}, request_body, loading)
}
export default { trigger, get }
