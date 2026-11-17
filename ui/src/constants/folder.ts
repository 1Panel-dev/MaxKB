/** 提供资源文件夹的全部与共享入口，全部入口使用当前工作空间 ID。 */

import type { FolderItem, FolderSource } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { getWorkspaceId } from '@/utils/resource-context'

export const FOLDER_ENTRY_ID = {
  get ALL() {
    return getWorkspaceId() ?? 'default'
  },
  SHARED: 'shared',
} as const

const folderEntryKeys = {
  [RESOURCE_TYPE.APPLICATION]: { all: 'application.categories.all', shared: 'application.categories.shared' },
  [RESOURCE_TYPE.KNOWLEDGE]: { all: 'knowledge.categories.all', shared: 'knowledge.categories.shared' },
  [RESOURCE_TYPE.TOOL]: { all: 'tool.categories.all', shared: 'tool.categories.shared' },
} as const satisfies Record<FolderSource, { all: string; shared: string }>

/** 选中的内置目录保留其 ID，页面读取名称时跟随当前语言。 */
export function getFolderEntry(source: FolderSource, entry: 'all' | 'shared', t: (key: string) => string): FolderItem {
  return {
    id: entry === 'all' ? FOLDER_ENTRY_ID.ALL : FOLDER_ENTRY_ID.SHARED,
    get name() {
      return t(folderEntryKeys[source][entry])
    },
  }
}
