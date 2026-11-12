/** 提供当前路由资源范围和工作空间上下文的读取函数。 */

import router from '@/router/admin'
import type { RouteLocationNormalized, RouteLocationNormalizedLoaded, RouteLocationResolvedGeneric } from 'vue-router'

type WorkspaceRouteLike = RouteLocationNormalized | RouteLocationNormalizedLoaded | RouteLocationResolvedGeneric

let hasRouteWorkspace = false
let routeWorkspaceId: string | undefined

const readWorkspaceId = (route: WorkspaceRouteLike): string | undefined => {
  const value = route.params.workspaceId
  return Array.isArray(value) ? value[0] : value
}

/**
 * 获取当前工作空间 id。
 * 取自目标路由参数；不在工作空间上下文下时返回 undefined。
 */
export const getWorkspaceId = (): string | undefined => (hasRouteWorkspace ? routeWorkspaceId : readWorkspaceId(router.currentRoute.value))

/**
 * 在给定路由的工作空间上下文内执行回调，期间 getWorkspaceId 使用该路由的 workspaceId。
 * 用于路由守卫评估目标路由权限：此时 router.currentRoute 尚未更新为待跳转路由，
 * 需要以被评估路由的参数为准，避免读到上一条（或初始 START）路由导致结果错误。
 */
export const withRouteWorkspace = <T>(route: WorkspaceRouteLike, fn: () => T): T => {
  const prevHas = hasRouteWorkspace
  const prevId = routeWorkspaceId
  hasRouteWorkspace = true
  routeWorkspaceId = readWorkspaceId(route)
  try {
    return fn()
  } finally {
    hasRouteWorkspace = prevHas
    routeWorkspaceId = prevId
  }
}

/** 判断当前路由是否属于工作空间资源。 */
export const isWorkspaceResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'workspace'
}

/** 判断当前路由是否属于工作空间共享资源。 */
export const isWorkspaceSharedResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'workspace-shared'
}

/** 判断当前路由是否属于 System 资源管理。 */
export const isSystemResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'system-resource'
}

/** 判断当前路由是否属于 System 共享资源。 */
export const isSystemSharedResource = () => {
  return router.currentRoute.value.meta.resourceScope === 'system-shared'
}

/** 获取当前是哪个资源范围 */
export const getResourceScope = () => {
  return router.currentRoute.value.meta.resourceScope
}
