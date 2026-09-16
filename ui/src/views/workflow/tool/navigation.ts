/** 工具工作流的返回导航，按资源范围返回对应列表。 */
import router from '@/router/admin'
import { getWorkspaceId, isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

/** 工作空间返回时携带所属目录，由列表的 FolderTree 恢复选中项。 */
export function goBack(folderId?: string | null) {
  if (isSystemResource()) {
    return router.push({ name: 'system-resource-tools' })
  }
  if (isSystemSharedResource()) {
    return router.push({ name: 'system-shared-tools' })
  }
  return router.push({
    name: 'workspace-tools',
    params: { workspaceId: getWorkspaceId() },
    query: folderId ? { folderId } : undefined,
  })
}
