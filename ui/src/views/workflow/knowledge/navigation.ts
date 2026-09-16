/** 知识库工作流返回导航。 */
import router from '@/router/admin'
import { getWorkspaceId, isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

/** Workspace 返回知识库详情，System 返回对应资源列表。 */
export function goBack(knowledgeId: string) {
  if (isSystemResource()) return router.push({ name: 'system-resource-knowledge' })
  if (isSystemSharedResource()) return router.push({ name: 'system-shared-knowledge' })
  return router.push({ name: 'workspace-knowledge-detail', params: { workspaceId: getWorkspaceId(), knowledgeId } })
}
