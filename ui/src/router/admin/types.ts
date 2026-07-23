export type RouteScope = 'workspace' | 'system'

declare module 'vue-router' {
  interface RouteMeta {
    scope?: RouteScope
    /** iconfont Symbol ID */
    icon?: string
    order?: number
    hidden?: boolean
    title?: string
  }
}
