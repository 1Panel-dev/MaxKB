import { RESOURCE_TYPE } from '@/api/enums'
import type { ShapeItem } from '@/workflow-canvas/types'

export type NodeMenuItem = ShapeItem & { height?: number }
export type NodeMenuResourceSource = typeof RESOURCE_TYPE.APPLICATION | typeof RESOURCE_TYPE.TOOL
export type NodeMenuTab = 'application' | 'basic' | 'tool'

export interface NodeMenuCurrentResource {
  id: string
  source: NodeMenuResourceSource
}
