/** 管理工作流编辑页的自动保存偏好缓存 key。 */

/** 按工作流类型与资源 ID 隔离自动保存开关，兼容已有缓存。 */
export function getWorkflowAutoSaveStorageKey(resourceType: 'application' | 'tool' | 'knowledge', resourceId: string) {
  return `workflowAutoSave:${resourceType}:${resourceId}`
}
