import knowledgeWorkspaceApi from '@/api/knowledge/knowledge'
import modelWorkspaceApi from '@/api/model/model'
import toolWorkspaceApi from '@/api/tool/tool'
import sharedWorkspaceApi from '@/api/shared-workspace'

// 普通 API
const workspaceApiMap = {
  knowledge: knowledgeWorkspaceApi,
  model: modelWorkspaceApi,
  tool: toolWorkspaceApi,
} as any

/** 动态导入 API 模块的函数
 *  loadSharedApi('knowledge', true)
 */

export function loadSharedApi(type: string, isShared?: boolean) {
  if (isShared) {
    // 共享 API
    return sharedWorkspaceApi
  } else {
    return workspaceApiMap[type]
  }
}
