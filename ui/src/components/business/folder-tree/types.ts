import type {
  WorkspaceFolder,
  WorkspaceFolderCreatePayload,
  WorkspaceFolderUpdatePayload,
} from '@/api/types'

export const FOLDER_SORT = {
  CREATE_TIME_ASC: 'create_time_asc',
  CREATE_TIME_DESC: 'create_time_desc',
  NAME_ASC: 'name_asc',
  NAME_DESC: 'name_desc',
} as const

export type FolderSort = (typeof FOLDER_SORT)[keyof typeof FOLDER_SORT]

export interface FolderFormSubmit {
  folderId?: string
  payload: WorkspaceFolderCreatePayload | WorkspaceFolderUpdatePayload
}

export interface FolderMoveSubmit {
  folder: WorkspaceFolder
  targetFolderId: string
}
