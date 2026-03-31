import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, postStream } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { AddInternalToolParam, toolData } from '@/api/type/tool'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/tool'
  },
})

/**
 * 工具列表带分页（无分页）
 * @params 参数 {folder_id: string}
 */
const getToolList: (
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<{ tools: any[]; folders: any[] }>> = (data, loading) => {
  return get(`${prefix.value}`, data, loading)
}

/**
 * 工具列表带分页（无分页）
 */
const getAllToolList: (
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<{ tools: any[]; folders: any[] }>> = (data, loading) => {
  return get(`${prefix.value}/tool_list`, data, loading)
}

/**
 * 工具列表带分页
 * @param 参数
 * param  {
 "folder_id": "string",
 "name": "string",
 "tool_type": "string",
 }
 */
const getToolListPage: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix.value}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建工具
 * @param 参数
 */
const postTool: (data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}`, data, undefined, loading)
}

/**
 * 修改工具
 * @param 参数

 */
const putTool: (tool_id: string, data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id,
  data,
  loading,
) => {
  return put(`${prefix.value}/${tool_id}`, data, undefined, loading)
}

/**
 * @param 参数
 */
const postToolTestConnection: (data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}/test_connection`, data, undefined, loading)
}

/**
 * 获取工具详情
 * @param tool_id 工具id
 * @param loading 加载器
 * @returns 函数详情
 */
const getToolById: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id,
  loading,
) => {
  return get(`${prefix.value}/${tool_id}`, undefined, loading)
}

/**
 * 删除工具
 * @param 参数 tool_id
 */
const delTool: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  tool_id,
  loading,
) => {
  return del(`${prefix.value}/${tool_id}`, undefined, {}, loading)
}

const putToolIcon: (id: string, data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  id,
  data,
  loading,
) => {
  return put(`${prefix.value}/${id}/edit_icon`, data, undefined, loading)
}

const exportTool = (id: string, name: string, loading?: Ref<boolean>) => {
  return exportFile(name + '.tool', `${prefix.value}/${id}/export`, undefined, loading)
}

/**
 * 调试工具
 * @param 参数

 */
const postToolDebug: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data: any,
  loading,
) => {
  return post(`${prefix.value}/debug`, data, undefined, loading)
}

const postImportTool: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}/import`, data, undefined, loading)
}

const postPylint: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return post(`${prefix.value}/pylint`, { code }, {}, loading)
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

const updateStoreTool: (
  tool_id: string,
  param: AddInternalToolParam,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, param, loading) => {
  return post(`${prefix.value}/${tool_id}/update_store_tool`, param, undefined, loading)
}

const pageToolRecord = (tool_id: string, page: pageRequest, param: any, loading?: Ref<boolean>) => {
  return get(
    `${prefix.value}/${tool_id}/tool_record/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

const getToolRecordDetail = (tool_id: string, record_id: string) => {
  return get(`${prefix.value}/${tool_id}/tool_record/${record_id}`)
}

const uploadSkillFile: (data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return put(`${prefix.value}/upload_skill_file`, data, undefined, loading)
}
/**
 * 保存工具工作流
 * @param tool_id
 * @param data
 * @param loading
 * @returns
 */
const putToolWorkflow: (
  tool_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, data, loading) => {
  return put(`${prefix.value}/${tool_id}/workflow`, data, undefined, loading)
}

/**
 * 导出知识库工作流
 * @param knowledge_id
 * @param knowledge_name
 * @param loading
 * @returns
 */
const exportKnowledgeWorkflow = (
  knowledge_id: string,
  knowledge_name: string,
  loading?: Ref<boolean>,
) => {
  return exportFile(
    knowledge_name + '.kbwf',
    `${prefix.value}/${knowledge_id}/workflow/export`,
    undefined,
    loading,
  )
}

/**
 * 导入工具工作流
 */
const importToolWorkflow: (
  tool_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, data, loading) => {
  return post(`${prefix.value}/${tool_id}/workflow/import`, data, undefined, loading)
}
/**
 * 获取工具工作流版本列表
 * @param tool_id
 * @param loading
 * @returns
 */
const listToolWorkflowVersion: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id: string,
  loading,
) => {
  return get(`${prefix.value}/${tool_id}/tool_version`, {}, loading)
}
/**
 *
 * @param tool_id 工具id
 * @param tool_version_id 工具版本id
 * @param data 数据
 * @param loading
 * @returns
 */
const updateToolWorkflowVersion: (
  tool_id: string,
  tool_version_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id: string, tool_version_id, data, loading) => {
  return put(`${prefix.value}/${tool_id}/tool_version/${tool_version_id}`, data, {}, loading)
}
const publish: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id: string,
  loading,
) => {
  return put(`${prefix.value}/${tool_id}/publish`, {}, {}, loading)
}

/**
 * 调试工作流
 * @param 参数
 * chat_id: string
 * data
 */
const debugToolWorkflow: (tool_id: string, data: any) => Promise<any> = (tool_id, data) => {
  const p = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  return postStream(`${p}${prefix.value}/${tool_id}/debug`, data)
}

const generateCode: (data: any) => Promise<Result<any>> = (data: any) => {
  const p = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  return postStream(`${p}${prefix.value}/generate_code`, data)
}
/**
 * mcp 节点
 */
const getMcpTools: (
  tool_id: string,
  mcp_servers: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (tool_id, mcp_servers, loading) => {
  return post(`${prefix.value}/${tool_id}/mcp_tools`, { mcp_servers }, {}, loading)
}
export default {
  getToolList,
  getAllToolList,
  getToolListPage,
  putTool,
  getToolById,
  postTool,
  postToolDebug,
  postImportTool,
  postPylint,
  exportTool,
  putToolIcon,
  delTool,
  addInternalTool,
  addStoreTool,
  updateStoreTool,
  postToolTestConnection,
  pageToolRecord,
  getToolRecordDetail,
  uploadSkillFile,
  putToolWorkflow,
  importToolWorkflow,
  listToolWorkflowVersion,
  updateToolWorkflowVersion,
  publish,
  debugToolWorkflow,
  generateCode,
  getMcpTools,
}
