import type { RouteLocationRaw } from 'vue-router'

export interface LayoutMenuItem {
  key: string
  label: string
  icon?: string
  route?: RouteLocationRaw
  children?: LayoutMenuItem[]
}

export type LayoutMode = 'workspace' | 'system'
