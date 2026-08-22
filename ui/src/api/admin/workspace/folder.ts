import { del, get, post, put } from '../core/request'
import type { FolderSource, FolderItem, RequestParams, FolderPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = (source: FolderSource) => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/${source}/folder`
}

/** 获取指定资源模块的 Workspace 文件夹树。 */
const getFolderTree = (source: FolderSource, query?: RequestParams) => {
  return get<FolderItem[]>(getPrefix(source), query)
}

/** 更新 Workspace 的文件夹。 */
const putFolder = (folderId: string, source: FolderSource, payload?: FolderPayload) => {
  return put<FolderPayload, FolderItem>(`${getPrefix(source)}/${folderId}`, payload)
}

/** 在指定资源模块中创建 Workspace 文件夹。 */
const postFolder = (source: FolderSource, payload: FolderPayload) => {
  return post<FolderPayload, FolderItem>(getPrefix(source), payload)
}

/** 删除指定 Workspace 文件夹及其中的资源。 */
const deleteFolder = (folderId: string, source: FolderSource) => {
  return del<boolean>(`${getPrefix(source)}/${folderId}`)
}

export default {
  deleteFolder,
  getFolderTree,
  postFolder,
  putFolder,
}
