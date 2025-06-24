import knowledgeWorkspaceApi from '@/api/knowledge/knowledge'
import modelWorkspaceApi from '@/api/model/model'
import toolWorkspaceApi from '@/api/tool/tool'
import sharedWorkspaceApi from '@/api/shared-workspace'
import toolSystemShareApi from '@/api/system-shared/tool'
import modelSystemShareApi from '@/api/system-shared/model'
import knowledgeSystemShareApi from '@/api/system-shared/knowledge'

// 普通 API
const workspaceApiMap = {
  knowledge: knowledgeWorkspaceApi,
  model: modelWorkspaceApi,
  tool: toolWorkspaceApi,
} as any

// 系统分享 API
const systemShareApiMap = {
  knowledge: knowledgeSystemShareApi,
  model: modelSystemShareApi,
  tool: toolSystemShareApi,
} as any

// 资源管理 API
const systemManageApiMap = {
  // knowledge: knowledgeWorkspaceApi,
  // model: modelWorkspaceApi,
  // tool: toolSystemShareApi,
} as any

const data = {
  systemShare: systemShareApiMap,
  workspace: workspaceApiMap,
  systemManage: systemManageApiMap,
}
/** 动态导入 API 模块的函数
 *  loadSharedApi('knowledge', true,'systemShare')
 */
export function loadSharedApi({
  type,
  isShared,
  systemType,
}: {
  type: string
  isShared?: boolean | undefined
  systemType?: 'systemShare' | 'workspace' | 'systemManage'
}) {
  if (isShared) {
    // 共享 API
    return sharedWorkspaceApi
  } else {
    return data[systemType || 'workspace'][type]
  }
}
