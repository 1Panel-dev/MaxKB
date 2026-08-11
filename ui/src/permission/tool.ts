/**
 * 工具资源权限映射
 */
export const toolPermissions = {
  edit: ['SYSTEM_RESOURCE_TOOL:READ+EDIT'],
  initParam: ['SYSTEM_RESOURCE_TOOL:READ+INIT_PARAM'],
  auth: ['SYSTEM_RESOURCE_TOOL:READ+AUTH'],
  triggerRead: ['SYSTEM_RESOURCE_TOOL:READ+TRIGGER_READ'],
  relateMap: ['SYSTEM_RESOURCE_TOOL:READ+RELATE_VIEW'],
  transfer: ['SYSTEM_RESOURCE_TOOL:READ+TRANSFER'],
  delete: ['SYSTEM_RESOURCE_TOOL:READ+DELETE'],
}

export type ToolPermissionKey = keyof typeof toolPermissions
