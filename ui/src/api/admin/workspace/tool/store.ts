import { post } from '../../core/request'
import type { AddStoreToolPayload, ToolItem, UpdateStoreToolPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getToolPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 将商店工具添加到当前工作空间。 */
const postStoreTool = (toolId: string, payload: AddStoreToolPayload) => {
  return post<AddStoreToolPayload, ToolItem>(`${getToolPrefix()}/${toolId}/add_store_tool`, payload)
}

/** 将工作空间中的商店工具更新到最新版本。 */
const postStoreToolUpdate = (toolId: string, payload: UpdateStoreToolPayload) => {
  return post<UpdateStoreToolPayload, ToolItem>(`${getToolPrefix()}/${toolId}/update_store_tool`, payload)
}

export default { postStoreTool, postStoreToolUpdate }
