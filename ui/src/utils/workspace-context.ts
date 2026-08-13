/** 提供当前工作空间上下文的读取函数（来源为实现细节，调用方无需关心）。 */

import router from '@/router/admin'

/**
 * 获取当前工作空间 id。
 * 供工具函数、权限判定等非组件环境读取当前工作空间；组件内可直接用 `useRoute()`。
 * 当前实现取自路由参数（依据「workspaceId 只以当前路由参数为准」的约定），
 * 若来源变更，调用方无需改动。
 * @returns 当前工作空间 id；不在工作空间上下文下时为 undefined。
 */
export const getWorkspaceId = (): string | undefined => {
  const value = router.currentRoute.value.params.workspaceId
  return Array.isArray(value) ? value[0] : value
}
