/** Admin Router 的业务范围和路由元信息声明。 */

import type { ResourceAuthorizationType } from '@/api/types'

export type RouteScope = 'workspace' | 'system'
export type ResourceScope = 'workspace' | 'system-resource' | 'system-shared'

declare module 'vue-router' {
  interface RouteMeta {
    scope?: RouteScope
    /** 当前页面使用的资源范围，用于区分 Workspace、System 资源管理和 System 共享资源。 */
    resourceScope?: ResourceScope
    /** 侧栏菜单激活状态的 iconfont Symbol ID */
    activeIcon?: string
    /** 侧栏需要保持激活的菜单路径 */
    activeMenu?: string
    /** iconfont Symbol ID */
    icon?: string
    order?: number
    hidden?: boolean
    /** 系统资源授权页面当前管理的资源类型。 */
    resource?: ResourceAuthorizationType
    title?: string
  }
}
