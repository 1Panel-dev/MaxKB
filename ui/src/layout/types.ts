/** 应用布局和菜单使用的类型。 */

import type { RouteLocationRaw ,RouteLocationNormalizedLoaded,RouteLocationNormalized} from 'vue-router'
 
export interface LayoutMenuItem {
  name: string
  label: string
  activeIcon?: string
  icon?: string
  route?: RouteLocationRaw
  permission?:(route?:RouteLocationNormalized | RouteLocationNormalizedLoaded)=>boolean
  children?: LayoutMenuItem[]
}

export type LayoutMode = 'workspace' | 'system'
