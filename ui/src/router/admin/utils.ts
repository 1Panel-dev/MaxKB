import type { RouteRecordRaw } from 'vue-router'
import type { LayoutMenuItem } from '@/layout/types'
import type { RouteScope } from './types'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'

const scopedRoutes: RouteRecordRaw[] = [workspaceRoutes, systemRoutes]

export function isWorkspace(scope?: RouteScope) {
  return scope === 'workspace'
}
export function isSystem(scope?: RouteScope) {
  return scope === 'system'
}

/** 根据 Workspace 或 System 路由树递归生成侧栏目录。 */
export function getChildRouteList(scope: RouteScope): LayoutMenuItem[] {
  const rootRoute = scopedRoutes.find((route) => route.meta?.scope === scope)

  const createMenuItems = (routes: readonly RouteRecordRaw[]): LayoutMenuItem[] => {
    return routes
      .filter((route) => route.name && route.meta?.title && route.meta.hidden !== true)
      .sort(
        (a, b) =>
          (a.meta?.order ?? Number.MAX_SAFE_INTEGER) - (b.meta?.order ?? Number.MAX_SAFE_INTEGER),
      )
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

  return createMenuItems(rootRoute?.children ?? [])
}
