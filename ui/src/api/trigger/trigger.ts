import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { User, ResetPasswordRequest, CheckCodeRequest } from '@/api/type/user'
import type { Ref } from 'vue'
import type { KeyValue, pageRequest } from '@/api/type/common'
import useStore from '@/stores'
import type { TriggerData } from '../type/trigger'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/trigger'
  },
})

/**
 * 触发器列表
 * @param data
 * @param loading
 * @returns
 */
const getTriggerList: (data?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return get(`${prefix.value}`, data, loading)
}

/**
 * 触发器详情
 * @param trigger_id
 * @param loading
 * @returns
 */
const getTriggerDetail: (trigger_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  trigger_id,
  loading,
) => {
  return get(`${prefix.value}/${trigger_id}`, {}, loading)
}

/**
 * 创建触发器
 * @param data
 * @param loading
 * @returns
 */
const postTrigger: (data: TriggerData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}`, data, undefined, loading)
}

/**
 * 修改触发器
 * @param trigger_id
 * @param data
 * @param loading
 * @returns
 */
const putTrigger: (
  trigger_id: string,
  data: TriggerData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (trigger_id, data, loading) => {
  return put(`${prefix.value}/${trigger_id}`, data, undefined, loading)
}

/**
 * 删除触发器
 * @param trigger_id
 * @param loading
 * @returns
 */
const deleteTrigger: (trigger_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  trigger_id,
  loading,
) => {
  return del(`${prefix.value}/${trigger_id}`, undefined, {}, loading)
}

/**
 * 批量删除触发器
 * @param data
 * @param loading
 * @returns
 */
const delMulTrigger: (data: any, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  data: any,
  loading,
) => {
  return put(`${prefix.value}/batch_delete`, { id_list: data }, undefined, loading)
}

/**
 * 批量激活/禁用触发器
 * @param data
 * @param loading
 * @returns
 */
const activateMulTrigger: (data: any, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  data: any,
  loading,
) => {
  return put(
    `${prefix.value}/batch_activate`,
    { id_list: data.id_list, is_active: data.is_active },
    undefined,
    loading,
  )
}

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
/**
 * 分页查询触发器执行任务
 * @param trigger_id 触发器id
 * @param page       分页参数
 * @param param      查询参数
 * @param loading    记载器
 * @returns
 */
const pageTriggerTaskRecord = (
  trigger_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => {
  return get(
    `${prefix.value}/${trigger_id}/task_record/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

const getTriggerTaskRecordDetails = (
  trigger_id: string,
  trigger_task_id: string,
  trigger_task_record_id: string,
  loading?: Ref<boolean>,
) => {
  return get(
    `${prefix.value}/${trigger_id}/trigger_task/${trigger_task_id}/trigger_task_record/${trigger_task_record_id}`,
    {},
    loading,
  )
}
export default {
  pageTrigger,
  getTriggerList,
  postTrigger,
  getTriggerDetail,
  putTrigger,
  deleteTrigger,
  delMulTrigger,
  activateMulTrigger,
  pageTriggerTaskRecord,
  getTriggerTaskRecordDetails,
}
