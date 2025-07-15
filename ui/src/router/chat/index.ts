import { hasPermission } from '@/utils/permission/index'
import NProgress from 'nprogress'
import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw,
  type RouteRecordName,
} from 'vue-router'
import useStore from '@/stores'
import { routes } from '@/router/chat/routes'
NProgress.configure({ showSpinner: false, speed: 500, minimum: 0.3 })
const router = createRouter({
  history: createWebHistory(window.MaxKB?.prefix ? window.MaxKB?.prefix : import.meta.env.BASE_URL),
  routes: routes,
})

// 路由前置拦截器
router.beforeEach(
  async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    NProgress.start()
    if (to.path === '/404') {
      next()
      return
    }
    const { chatUser } = useStore()
    if (['login', 'chat'].includes(to.name ? to.name.toString() : '')) {
      chatUser.setAccessToken(to.params.accessToken.toString())
    } else {
      next({
        path: '/404',
      })
      return
    }
    let authentication = false
    try {
      authentication = await chatUser.isAuthentication()
    } catch (e: any) {
      next()
      return
    }
    const p_token = to.query.token
    if (p_token) {
      chatUser.setToken(p_token as string)
    }
    const token = chatUser.getToken()
    if (authentication) {
      if (!token && to.name != 'login') {
        next({
          name: 'login',
          params: {
            accessToken: to.params.accessToken,
          },
          query: to.query,
        })
        return
      } else {
        if (to.name == 'login') {
          next()
          return
        } else {
          try {
            await chatUser.applicationProfile()
            await chatUser.getChatUserProfile()
          } catch (e: any) {
            if (e.response?.status === 401) {
              next({
                name: 'login',
                params: {
                  accessToken: to.params.accessToken,
                },
                query: to.query,
              })
            }
            return
          }
          if (p_token) {
            const q = to.query
            delete q.token
            next({ ...to, query: q })
          } else {
            next()
          }
          return
        }
      }
    } else {
      try {
        await chatUser.anonymousAuthentication()
      } catch (e: any) {
        next()
        return
      }
    }
    if (!chatUser.application) {
      try {
        await chatUser.applicationProfile()
      } catch (e: any) {
        if (e.response?.status === 401) {
          next({
            name: 'login',
            params: {
              accessToken: to.params.accessToken,
            },
            query: to.query,
          })
        }
        return
      }
    }
    next()
  },
)
router.afterEach(() => {
  NProgress.done()
})

export const getChildRouteListByPathAndName = (path: any, name?: RouteRecordName | any) => {
  return getChildRouteList(routes, path, name)
}

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

export default router
