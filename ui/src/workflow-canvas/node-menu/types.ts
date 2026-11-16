import type { ShapeItem } from '@/workflow-canvas/types'
import { RESOURCE_TYPE } from '@/api/enums'

export type NodeMenuItem = ShapeItem & { height?: number }
export type NodeMenuResourceSource = typeof RESOURCE_TYPE.APPLICATION | typeof RESOURCE_TYPE.TOOL
export type NodeMenuTab = 'application' | 'basic' | 'data-source' | 'tool'
