/** 智能体工作流的返回导航，按详情路由配置选择可访问的子页面。 */
import type { RouteParamsGeneric } from 'vue-router'
import router from '@/router/admin'
import { APPLICATION_TYPE } from '@/api/enums'
import { getWorkspaceId, isSystemResource } from '@/utils/resource-context'

/** 按详情菜单顺序返回首个可访问的子路由，无可用详情时返回对应范围的列表。 */
export function goBack(applicationId: string) {
  const systemResource = isSystemResource()
  const detailRouteName = systemResource ? 'system-application-detail-layout' : 'workspace-application-detail-layout'
  const listRouteName = systemResource ? 'system-resource-applications' : 'workspace-application-list'
  const workspaceId = getWorkspaceId()
  const params: RouteParamsGeneric = { applicationId, type: APPLICATION_TYPE.WORK_FLOW }
  if (workspaceId) params.workspaceId = workspaceId

  const detailRoute = router.getRoutes().find(({ name }) => name === detailRouteName)
  const targetRoute = detailRoute?.children
    .filter((child) => child.name && child.meta?.title && !child.meta.hidden)
    .sort((left, right) => (left.meta?.order ?? Number.MAX_SAFE_INTEGER) - (right.meta?.order ?? Number.MAX_SAFE_INTEGER))
    .find((child) => child.meta?.canAccess?.(params) ?? true)

  if (targetRoute?.name) {
    return router.push({ name: targetRoute.name, params })
  }

  return router.push({ name: listRouteName, params: systemResource ? {} : { workspaceId } })
}
