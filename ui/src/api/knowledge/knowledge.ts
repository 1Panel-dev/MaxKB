import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'

/**
 * 获得知识库文件夹列表
 * @params 参数
 * {folder_id: string,
 * name: string,
 * user_id: string，
 * desc: string,}
 */
const getKnowledgeByFolder: (
  wordspace_id: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (wordspace_id, data, loading) => {
  return get(`${prefix}/${wordspace_id}/knowledge`, data, loading)
}

/**
 * 知识库列表
 * @param 参数
* param  {
            "folder_id": "string",
            "name": "string",
            "tool_type": "string",
            desc: string,
          }
 */
const getKnowledgeList: (
  wordspace_id: string,
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, page, param, loading) => {
  return get(
    `${prefix}/${wordspace_id}/knowledge/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

export default {
  getKnowledgeByFolder,
  getKnowledgeList,
}
