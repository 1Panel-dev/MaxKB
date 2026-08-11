/**
 * 智能体（应用）资源权限映射
 * permission ID 格式：{FEATURE_ID}:{ACTION}
 */
export const applicationPermissions = {
  setting: ['SYSTEM_RESOURCE_APPLICATION:READ+SETTING'],
  auth: ['SYSTEM_RESOURCE_APPLICATION:READ+AUTH'],
  relateMap: ['SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW'],
  triggerRead: ['SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ'],
  transfer: ['SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER'],
  export: ['SYSTEM_RESOURCE_APPLICATION:READ+EXPORT'],
  delete: ['SYSTEM_RESOURCE_APPLICATION:READ+DELETE'],
}

export type ApplicationPermissionKey = keyof typeof applicationPermissions
