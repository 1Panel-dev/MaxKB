import type { LayoutMode } from './types'

export function isWorkspace(mode?: LayoutMode) {
  return mode === 'workspace'
}

export function isSystem(mode?: LayoutMode) {
  return mode === 'system'
}
