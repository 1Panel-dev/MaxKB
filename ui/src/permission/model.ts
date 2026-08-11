/**
 * 模型资源权限映射
 */
export const modelPermissions = {
  edit: ['SYSTEM_RESOURCE_MODEL:READ+EDIT'],
  modelParam: ['SYSTEM_RESOURCE_MODEL:READ+MODEL_PARAM'],
  auth: ['SYSTEM_RESOURCE_MODEL:READ+AUTH'],
  relateMap: ['SYSTEM_RESOURCE_MODEL:READ+RELATE_VIEW'],
  delete: ['SYSTEM_RESOURCE_MODEL:READ+DELETE'],
}

export type ModelPermissionKey = keyof typeof modelPermissions
