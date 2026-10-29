/** 提供资源文件夹的全部与共享入口，全部入口使用当前工作空间 ID。 */

import { RESOURCE_TYPE } from '@/api/enums'
import type { FolderItem, FolderSource } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

export const FOLDER_ENTRY_ID = {
  get ALL() {
    return getWorkspaceId() ?? 'default'
  },
  SHARED: 'shared',
} as const

function createFolderEntries(resourceName: string) {
  return {
    all: {
      get id() {
        return FOLDER_ENTRY_ID.ALL
      },
      name: `全部${resourceName}`,
    },
    shared: { id: FOLDER_ENTRY_ID.SHARED, name: `共享${resourceName}` },
  }
}

export const FOLDER_ENTRIES = {
  [RESOURCE_TYPE.APPLICATION]: createFolderEntries('智能体'),
  [RESOURCE_TYPE.KNOWLEDGE]: createFolderEntries('知识库'),
  [RESOURCE_TYPE.TOOL]: createFolderEntries('工具'),
} satisfies Record<FolderSource, { all: FolderItem; shared: FolderItem }>
