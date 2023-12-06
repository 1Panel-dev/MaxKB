import { Result } from '@/request/Result'
import { get, post, postStream, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/application'
/**
 * 对话日志
 * @param 参数 
 * application_id, history_day
 * page  {
              "current_page": "string",
              "page_size": "string",
            }
* param  {
              "history_day": "string",
              "search": "string",
            }
 */
const getChatLog: (
  applicaiton_id: String,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, page, param, loading) => {
  return get(
    `${prefix}/${applicaiton_id}/chat/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

export default {
  getChatLog
}
