import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/system/resource'


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



export default {
  getFolder,

}
