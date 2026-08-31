import type { RouteLocationNormalizedLoaded, RouteMeta, RouteRecordName, RouteRecordRaw } from 'vue-router'
import type { LayoutMenuItem } from '@/layout/types'
import type { RouteScope } from './types'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'

interface MenuRouteRecord {
  children?: readonly MenuRouteRecord[]
  meta?: RouteMeta
  name?: RouteRecordName | null
}

const scopedRoutes: RouteRecordRaw[] = [workspaceRoutes, systemRoutes]

/** 将路由记录递归转换为 Layout 菜单。 */
function createMenuItems(routes: readonly MenuRouteRecord[]): LayoutMenuItem[] {
  return routes
    .filter((route) => route.name && route.meta?.title && route.meta.hidden !== true)
    .sort((a, b) => (a.meta?.order ?? Number.MAX_SAFE_INTEGER) - (b.meta?.order ?? Number.MAX_SAFE_INTEGER))
    .map((route) => {
      const children = route.children ? createMenuItems(route.children) : []

      return {
        name: String(route.name),
        label: route.meta!.title!,
        activeIcon: route.meta?.activeIcon,
        icon: route.meta?.icon,
        route: { name: route.name! },
        children: children.length ? children : undefined,
      }
    })
}

/** 根据 Workspace 或 System 路由树生成一级侧栏目录。 */
export function getChildRouteList(scope: RouteScope): LayoutMenuItem[] {
  const rootRoute = scopedRoutes.find((route) => route.meta?.scope === scope)

  return createMenuItems(rootRoute?.children ?? [])
}

/** 根据当前匹配路由生成所属详情父路由的二级侧栏目录。 */
export function getMatchedChildRouteList(route: RouteLocationNormalizedLoaded): LayoutMenuItem[] {
  const activeRouteName = route.meta.detailActiveMenu ?? route.name

  if (!activeRouteName) return []

  const parentRoute = [...route.matched]
    .reverse()
    .find((matchedRoute) => matchedRoute.children.some((childRoute) => childRoute.name === activeRouteName))

  return createMenuItems(parentRoute?.children ?? [])
}
