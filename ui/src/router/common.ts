import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw,
  type RouteRecordName,
} from 'vue-router'
import { hasPermission, set_next_route } from '@/utils/permission/index'
export const getChildRouteList: (
  routeList: Array<RouteRecordRaw>,
  path: string,
  name?: RouteRecordName | null | undefined,
) => Array<RouteRecordRaw> = (routeList, path, name) => {
  for (let index = 0; index < routeList.length; index++) {
    const route = routeList[index]
    if (name === route.name && path === route.path) {
      return route.children || []
    }
    if (route.children && route.children.length > 0) {
      const result = getChildRouteList(route.children, path, name)
      if (result && result?.length > 0) {
        return result
      }
    }
  }
  return []
}
/**
 * 获取同级路由
 * @param routeList
 * @param name
 * @returns
 */
export const getSameRouteList: (
  routeList: Array<RouteRecordRaw>,
  name?: RouteRecordName | null | undefined,
) => Array<RouteRecordRaw> = (routeList, name) => {
  for (let index = 0; index < routeList.length; index++) {
    const route = routeList[index]
    if (name === route.name) {
      return routeList
    }
    if (route.children && route.children.length > 0) {
      const result = getSameRouteList(route.children, name)
      if (result && result?.length > 0) {
        return result
      }
    }
  }
  return []
}

/**
 * 获取有权限的路由
 * @param routes
 * @param to
 * @returns
 */
export const getPermissionRoute = (routes: Array<RouteRecordRaw>, to: RouteLocationNormalized) => {
  const routeName: string = to.meta
    ? to.meta.permissionRoute
      ? (to.meta.permissionRoute as string)
      : (to.name as string)
    : (to.name as string)
  const routeList = getSameRouteList(routes, routeName)
  const route = routeList.find((route: any) => {
    return (
      (to.meta.group ? to.meta.group == route.meta.group : true) &&
      (route.meta.permission ? hasPermission(route.meta.permission as any, 'OR') : true)
    )
  })

  if (route?.name) {
    return { name: route?.name, params: to.params }
  }
  return { name: 'noPermission' }
}
