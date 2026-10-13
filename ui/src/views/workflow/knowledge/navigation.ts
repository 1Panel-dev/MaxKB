/** 知识库工作流返回导航。 */
import router from '@/router/admin'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import type { KnowledgeDetail } from '@/api/types'
import { getWorkspaceId, getResourceScope } from '@/utils/resource-context'

/** 返回当前资源范围的知识库详情。 */
export function goBack(knowledgeId: string, type: KnowledgeDetail['type'] = KNOWLEDGE_TYPE.WORKFLOW) {
  const scope = getResourceScope()
  if (!scope) throw new Error('Knowledge resource scope is unavailable')
  const name = `${scope}-knowledge-detail`
  const params =
    scope === 'workspace' || scope === 'workspace-shared'
      ? { workspaceId: getWorkspaceId(), knowledgeId, type: KNOWLEDGE_TYPE_MAP[type] }
      : { knowledgeId, type: KNOWLEDGE_TYPE_MAP[type] }
  return router.push({ name, params, query: router.currentRoute.value.query })
}
