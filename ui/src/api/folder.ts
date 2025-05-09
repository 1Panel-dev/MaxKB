import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'

/**
 * 获得知识库文件夹列表
 * @params 参数
 *  source : APPLICATION, KNOWLEDGE, TOOL
 * {name: string}
 */
const getFolder: (
  wordspace_id: string,
  source: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (wordspace_id, source, data, loading) => {
  return get(`${prefix}/${wordspace_id}/${source}/folder`, data, loading)
}

export default {
  getFolder,
}
