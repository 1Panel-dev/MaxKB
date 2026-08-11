/**
 * 知识库资源权限映射
 */
export const knowledgePermissions = {
  vector: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+VECTOR'],
  generate: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+GENERATE'],
  auth: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+AUTH'],
  relateMap: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+RELATE_VIEW'],
  transfer: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+TRANSFER'],
  setting: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+SETTING'],
  export: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+EXPORT'],
  delete: ['SYSTEM_RESOURCE_KNOWLEDGE:READ+DELETE'],
}

export type KnowledgePermissionKey = keyof typeof knowledgePermissions
