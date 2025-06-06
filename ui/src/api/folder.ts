import {Result} from '@/request/Result'
import {get, post, del, put} from '@/request/index'
import {type Ref} from 'vue'
import type {pageRequest} from '@/api/type/common'

const prefix = '/workspace/' + localStorage.getItem('workspace_id')

/**
 * 获得文件夹列表
 * @params 参数
 *  source : APPLICATION, KNOWLEDGE, TOOL
 *  data : {name: string}
 */
const getFolder: (
  source: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (source, data, loading) => {
  return get(`${prefix}/${source}/folder`, data, loading)
}

/**
 * 添加文件夹
 * @params 参数
 *  source : APPLICATION, KNOWLEDGE, TOOL
 {
 "name": "string",
 "desc": "string",
 "parent_id": "root"
 }
 */
const postFolder: (
  source: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (source, data, loading) => {
  return post(`${prefix}/${source}/folder`, data, loading)
}

export default {
  getFolder,
  postFolder,
}
