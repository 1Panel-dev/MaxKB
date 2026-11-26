/** 管理目录树按用户、工作空间与资源类型隔离的排序缓存 key。 */
import type { FolderSource } from '@/api/types'

/** 按用户、工作空间和资源类型生成文件夹自定义排序 key。 */
export function getFolderCustomSortStorageKey(userId: string | undefined, workspaceId: string | undefined, source: FolderSource) {
  return `${userId}-${workspaceId}-${source}-folder-custom-sort`
}

/** 按用户、工作空间和资源类型生成文件夹排序方式 key。 */
export function getFolderSortTypeStorageKey(userId: string | undefined, workspaceId: string | undefined, source: FolderSource) {
  return `${userId}-${workspaceId}-${source}-folder-sort-type`
}
