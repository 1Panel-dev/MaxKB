/** 应用布局和菜单使用的数据类型。 */

import type { RouteLocationRaw } from 'vue-router'

export interface LayoutMenuItem {
  name: string
  label: string
  activeIcon?: string
  icon?: string
  route?: RouteLocationRaw
  children?: LayoutMenuItem[]
}

export type LayoutMode = 'workspace' | 'system'
