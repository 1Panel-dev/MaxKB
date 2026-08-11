import { applicationPermissions } from './application'
import { knowledgePermissions } from './knowledge'
import { toolPermissions } from './tool'
import { modelPermissions } from './model'

export const permissionMap = {
  application: applicationPermissions,
  knowledge: knowledgePermissions,
  tool: toolPermissions,
  model: modelPermissions,
}

export type ResourceType = keyof typeof permissionMap
