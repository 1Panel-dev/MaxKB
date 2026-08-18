import { del, get, post, put } from '../core/request'
import type {
  FolderSource,
  WorkspaceFolder,
  WorkspaceFolderCreatePayload,
  WorkspaceFolderQuery,
  WorkspaceFolderUpdatePayload,
} from '@/api/types'

const getPrefix = (workspaceId: string, source: FolderSource) =>
  `/workspace/${workspaceId}/${source}/folder`

/** 获取指定资源模块的 Workspace 文件夹树。 */
const getFolderTree = (workspaceId: string, source: FolderSource, query?: WorkspaceFolderQuery) => {
  return get<WorkspaceFolder[]>(getPrefix(workspaceId, source), query)
}

/** 获取指定 Workspace 文件夹详情。 */
const getFolderDetail = (workspaceId: string, source: FolderSource, folderId: string) => {
  return get<WorkspaceFolder>(`${getPrefix(workspaceId, source)}/${folderId}`)
}

/** 在指定资源模块中创建 Workspace 文件夹。 */
const postFolder = (
  workspaceId: string,
  source: FolderSource,
  payload: WorkspaceFolderCreatePayload,
) => {
  return post<WorkspaceFolderCreatePayload, WorkspaceFolder>(
    getPrefix(workspaceId, source),
    payload,
  )
}

/** 更新指定 Workspace 文件夹。 */
const putFolder = (
  workspaceId: string,
  source: FolderSource,
  folderId: string,
  payload: WorkspaceFolderUpdatePayload,
) => {
  return put<WorkspaceFolderUpdatePayload, WorkspaceFolder>(
    `${getPrefix(workspaceId, source)}/${folderId}`,
    payload,
  )
}

/** 删除指定 Workspace 文件夹及其中的资源。 */
const deleteFolder = (workspaceId: string, source: FolderSource, folderId: string) => {
  return del<undefined, boolean>(`${getPrefix(workspaceId, source)}/${folderId}`)
}

export default {
  deleteFolder,
  getFolderDetail,
  getFolderTree,
  postFolder,
  putFolder,
}
