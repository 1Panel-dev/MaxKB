/** 提供资源文件夹的全部与共享入口，全部入口使用当前工作空间 ID。 */

import { getWorkspaceId } from '@/utils/resource-context'

export const FOLDER_ENTRY_ID = {
  get ALL() {
    return getWorkspaceId() ?? 'default'
  },
  SHARED: 'shared',
} as const
