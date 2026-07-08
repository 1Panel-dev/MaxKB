import { Result } from '@/request/Result'
import { get, post, del, put, exportFile } from '@/request/index'
import { type Ref } from 'vue'
import type { TriggerData } from '../type/trigger'



const prefix = 'system/resource'


/**
 * 资源端创建触发器
 * @param source_type  资源类型
 * @param source_id    资源id
 * @param data         数据
 * @param loading      加载器
 * @returns
 */
const postResourceTrigger: (
  source_type: string,
  source_id: string,
  data: TriggerData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (source_type, source_id, data, loading) => {
  return post(
    `${prefix}/${source_type}/${source_id}/trigger`,
    data,
    undefined,
    loading,
  )
}

/**
 * 资源端触发器列表
 * @param source_type
 * @param source_id
 * @param loading
 * @returns
 */
const getResourceTriggerList: (
  source_type: string,
  source_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (source_type, source_id, loading) => {
  return get(
    `${prefix}/${source_type}/${source_id}/trigger`,
    undefined,
    loading
  )
}

/**
 * 资源端触发器详情
 * @param source_type
 * @param source_id
 * @param trigger_id
 * @param loading
 * @returns
 */
const getResourceTriggerDetail: (
    source_type: string,
  source_id: string,
  trigger_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (source_type, source_id, trigger_id, loading) => {
  return get(
    `${prefix}/${source_type}/${source_id}/trigger/${trigger_id}`,
    undefined,
    loading
  )
}

/**
 * 资源端删除触发器
 * @param source_type
 * @param source_id
 * @param trigger_id
 * @param loading
 * @returns
 */
const deleteResourceTrigger: (
    source_type: string,
  source_id: string,
  trigger_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (source_type, source_id, trigger_id, loading) => {
  return del(
    `${prefix}/${source_type}/${source_id}/trigger/${trigger_id}`,
    undefined,
    {},
    loading
  )
}

/**
 * 资源端修改触发器
 * @param source_type 资源类型
 * @param source_id   资源id
 * @param trigger_id  触发器id
 * @param data        触发器数据
 * @param loading     加载器
 * @returns
 */
const putResourceTrigger: (
  source_type: string,
  source_id: string,
  trigger_id: string,
  data: TriggerData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (source_type, source_id, trigger_id, data, loading) => {
  return put(
    `${prefix}/${source_type}/${source_id}/trigger/${trigger_id}`,
    data,
    undefined,
    loading,
  )
}

export default {
  postResourceTrigger,
  getResourceTriggerList,
  getResourceTriggerDetail,
  deleteResourceTrigger,
  putResourceTrigger
}
