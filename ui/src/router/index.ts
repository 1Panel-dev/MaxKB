import { hasPermission } from '@/common/permission/index'
import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw
} from 'vue-router'
import { useUserStore } from '@/stores/user'
import { store } from '@/stores'
import { routes } from '@/router/data'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

//  解决刷新获取用户信息问题
let userStore: any = null

// 路由前置拦截器
router.beforeEach(
  async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    if (to.name === '404') {
      next()
      return
    }
    if (userStore === null) {
      userStore = useUserStore(store)
    }
    const notAuthRouteNameList = ['register', 'login', 'forgot_password', 'reset_password']

    if (!notAuthRouteNameList.includes(to.name ? to.name.toString() : '')) {
      const token = userStore.getToken()
      if (!token) {
        next({
          path: '/login'
        })
        return
      }
      if (!userStore.userInfo) {
        await userStore.profile()
      }
    }
    // 判断是否有菜单权限
    if (to.meta.permission ? hasPermission(to.meta.permission as any, 'OR') : true) {
      next()
    } else {
      // 如果没有权限则直接取404页面
      next('404')
    }
  }
)

export const getChildRouteListByPathAndName = (path: string, name: string) => {
  return getChildRouteList(routes, path, name)
}

export const getChildRouteList: (
  routeList: Array<RouteRecordRaw>,
  path: string,
  name: string
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

export default router
