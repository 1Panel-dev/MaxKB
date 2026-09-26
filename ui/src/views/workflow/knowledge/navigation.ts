/** 知识库工作流返回导航。 */
import router from '@/router/admin'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import type { KnowledgeDetail } from '@/api/types'
import { getWorkspaceId, isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

/** Workspace 返回知识库详情，System 返回对应资源列表。 */
export function goBack(knowledgeId: string, type: KnowledgeDetail['type'] = KNOWLEDGE_TYPE.WORKFLOW) {
  if (isSystemResource()) return router.push({ name: 'system-resource-knowledge' })
  if (isSystemSharedResource()) return router.push({ name: 'system-shared-knowledge' })
  return router.push({ name: 'workspace-knowledge-detail', params: { workspaceId: getWorkspaceId(), knowledgeId, type: KNOWLEDGE_TYPE_MAP[type] } })
}
