import { Result } from '@/request/Result'
import { get, post, del, put, exportFile } from '@/request/index'
import { type Ref } from 'vue'
import type { AddInternalToolParam } from '@/api/type/tool'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/tool'
  },
})

/**
 * 工具商店-系统内置列表
 */
const getInternalToolList: (param?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  param,
  loading,
) => {
  return get('/workspace/internal/tool', param, loading)
}

/**
 * 工具商店列表
 */
const getStoreToolList: (param?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  param,
  loading,
) => {
  return get('/workspace/store/tool', param, loading)
}

/**
 * 工具商店-添加系统内置
 */
const addInternalTool: (
  tool_id: string,
  param: AddInternalToolParam,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, param, loading) => {
  return post(`${prefix.value}/${tool_id}/add_internal_tool`, param, undefined, loading)
}

/**
 * 工具商店-添加
 */
const addStoreTool: (
  tool_id: string,
  param: AddInternalToolParam,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, param, loading) => {
  return post(`${prefix.value}/${tool_id}/add_store_tool`, param, undefined, loading)
}

export default {
  getInternalToolList,
  getStoreToolList,
  addInternalTool,
  addStoreTool
}
