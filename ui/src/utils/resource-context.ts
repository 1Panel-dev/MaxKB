/** 提供当前路由资源范围和工作空间上下文的读取函数。 */

import router from '@/router/admin'

/**
 * 获取当前工作空间 id。
 * 当前实现取自路由参数；不在工作空间上下文下时返回 undefined。
 */
export const getWorkspaceId = (): string | undefined => {
  const value = router.currentRoute.value.params.workspaceId
  return Array.isArray(value) ? value[0] : value
}

/** 判断当前路由是否属于工作空间资源。 */
export const isWorkspaceResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'workspace'
}

/** 判断当前路由是否属于 System 资源管理。 */
export const isSystemResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'system-resource'
}

/** 判断当前路由是否属于 System 共享资源。 */
export const isSystemSharedResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'system-shared'
}
