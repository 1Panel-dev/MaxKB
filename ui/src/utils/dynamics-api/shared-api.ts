import knowledgeWorkspaceApi from '@/api/knowledge/knowledge'
import documentWorkspaceApi from '@/api/knowledge/document'
import paragraphWorkspaceApi from '@/api/knowledge/paragraph'
import problemWorkspaceApi from '@/api/knowledge/problem'
import modelWorkspaceApi from '@/api/model/model'
import toolWorkspaceApi from '@/api/tool/tool'
import chatUserWorkspaceApi from '@/api/chat-user/chat-user'
import sharedWorkspaceApi from '@/api/shared-workspace'
import toolSystemShareApi from '@/api/system-shared/tool'
import modelSystemShareApi from '@/api/system-shared/model'
import knowledgeSystemShareApi from '@/api/system-shared/knowledge'
import documentSystemShareApi from '@/api/system-shared/document'
import paragraphSystemShareApi from '@/api/system-shared/paragraph'
import problemSystemShareApi from '@/api/system-shared/problem'
import chatUserSystemShareApi from '@/api/system-shared/chat-user'
import workspaceApi from '@/api/workspace/workspace'
import systemUserApi from '@/api/user/user'
import workspaceShare from '@/permission/knowledge/workspace-share'

// 普通 API
const workspaceApiMap = {
  knowledge: knowledgeWorkspaceApi,
  model: modelWorkspaceApi,
  tool: toolWorkspaceApi,
  document: documentWorkspaceApi,
  paragraph: paragraphWorkspaceApi,
  problem: problemWorkspaceApi,
  chatUser: chatUserWorkspaceApi,
  workspace: workspaceApi,
} as any

// 系统分享 API
const systemShareApiMap = {
  knowledge: knowledgeSystemShareApi,
  model: modelSystemShareApi,
  tool: toolSystemShareApi,
  document: documentSystemShareApi,
  paragraph: paragraphSystemShareApi,
  problem: problemSystemShareApi,
  chatUser: chatUserSystemShareApi,
  workspace: systemUserApi, // 共享的应该查全部人吧
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
  workspaceShare: workspaceApiMap
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
  systemType?: 'systemShare' | 'workspace' | 'systemManage' | 'workspaceShare'
}) {
  if (isShared) {
    // 共享 API
    return sharedWorkspaceApi
  } else {
    return data[systemType || 'workspace'][type]
  }
}
