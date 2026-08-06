/** Admin Router 的业务范围和路由元信息声明。 */

export type RouteScope = 'workspace' | 'system'

declare module 'vue-router' {
  interface RouteMeta {
    scope?: RouteScope
    /** 侧栏菜单激活状态的 iconfont Symbol ID */
    activeIcon?: string
    /** 侧栏需要保持激活的菜单路径 */
    activeMenu?: string
    /** iconfont Symbol ID */
    icon?: string
    order?: number
    hidden?: boolean
    title?: string
  }
}
