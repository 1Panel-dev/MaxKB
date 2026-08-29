import { post } from '../../core/request'
import type {
  AddInternalToolPayload,
  AddStoreToolPayload,
  ToolItem,
  UpdateStoreToolPayload,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getToolPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 将系统内置工具添加到当前工作空间。 */
const postInternalTool = (toolId: string, payload: AddInternalToolPayload) => {
  return post<AddInternalToolPayload, ToolItem>(
    `${getToolPrefix()}/${toolId}/add_internal_tool`,
    payload,
  )
}

/** 将商店工具添加到当前工作空间。 */
const postStoreTool = (toolId: string, payload: AddStoreToolPayload) => {
  return post<AddStoreToolPayload, ToolItem>(`${getToolPrefix()}/${toolId}/add_store_tool`, payload)
}

/** 将工作空间中的商店工具更新到最新版本。 */
const postStoreToolUpdate = (toolId: string, payload: UpdateStoreToolPayload) => {
  return post<UpdateStoreToolPayload, ToolItem>(
    `${getToolPrefix()}/${toolId}/update_store_tool`,
    payload,
  )
}

export default {
  postInternalTool,
  postStoreTool,
  postStoreToolUpdate,
}
