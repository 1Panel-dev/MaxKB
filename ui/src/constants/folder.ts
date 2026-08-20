import { FOLDER_SOURCE } from '@/api/enums'
import type { FolderItem, FolderSource } from '@/api/types'

export const FOLDER_ENTRY_ID = {
  ALL: 'default',
  SHARED: 'shared',
} as const

export const FOLDER_ENTRIES = {
  [FOLDER_SOURCE.APPLICATION]: {
    all: { id: FOLDER_ENTRY_ID.ALL, name: '全部智能体' },
    shared: { id: FOLDER_ENTRY_ID.SHARED, name: '共享智能体' },
  },
  [FOLDER_SOURCE.KNOWLEDGE]: {
    all: { id: FOLDER_ENTRY_ID.ALL, name: '全部知识库' },
    shared: { id: FOLDER_ENTRY_ID.SHARED, name: '共享知识库' },
  },
  [FOLDER_SOURCE.TOOL]: {
    all: { id: FOLDER_ENTRY_ID.ALL, name: '全部工具' },
    shared: { id: FOLDER_ENTRY_ID.SHARED, name: '共享工具' },
  },
} satisfies Record<FolderSource, { all: FolderItem; shared: FolderItem }>
