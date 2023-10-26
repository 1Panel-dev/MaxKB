import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { datasetListRequest } from '@/api/type/dataset'

const prefix = '/dataset'

/**
 * 获取分页数据集
 * @param 参数  {
              "current_page": "string",
              "page_size": "string",
              "search_text": "string",
            }
 */
const getDateset: (param: datasetListRequest) => Promise<Result<any[]>> = (param) => {
  return get(`${prefix}`, param)
}

/**
 * 获取全部数据集
 * @param 参数 search_text
 */
const getAllDateset: (param?: String) => Promise<Result<any[]>> = (param) => {
  return get(`${prefix}`, param && { search_text: param })
}

/**
 * 删除数据集
 * @param 参数 dataset_id
 */
const delDateset: (dataset_id: String) => Promise<Result<boolean>> = (dataset_id) => {
  return del(`${prefix}/${dataset_id}`)
}


export default {
  getDateset,
  getAllDateset,
  delDateset
}
