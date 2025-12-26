import knowledgeWorkspaceApi from '@/api/knowledge/knowledge'
import documentWorkspaceApi from '@/api/knowledge/document'
import paragraphWorkspaceApi from '@/api/knowledge/paragraph'
import problemWorkspaceApi from '@/api/knowledge/problem'
import resourceMappingApi from '@/api/workspace/resource-mapping'
import modelWorkspaceApi from '@/api/model/model'
import toolWorkspaceApi from '@/api/tool/tool'
import chatUserWorkspaceApi from '@/api/chat-user/chat-user'
import applicationWorkspaceApi from '@/api/application/application'
import applicationKeyWorkspaceApi from '@/api/application/application-key'
import workflowVersionWorkspaceApi from '@/api/application/workflow-version'
import chatLogWorkspaceApi from '@/api/application/chat-log'
import resourceAuthorizationWorkspaceApi from '@/api/workspace/resource-authorization'
import sharedWorkspaceApi from '@/api/shared-workspace'
import toolSystemShareApi from '@/api/system-shared/tool'
import modelSystemShareApi from '@/api/system-shared/model'
import knowledgeSystemShareApi from '@/api/system-shared/knowledge'
import documentSystemShareApi from '@/api/system-shared/document'
import paragraphSystemShareApi from '@/api/system-shared/paragraph'
import problemSystemShareApi from '@/api/system-shared/problem'
import chatUserSystemShareApi from '@/api/system-shared/chat-user'
import workspaceApi from '@/api/workspace/workspace'
import folderWorkspaceApi from '@/api/workspace/folder'
import systemUserApi from '@/api/user/user'
import ToolResourceApi from '@/api/system-resource-management/tool'
import knowledgeResourceApi from '@/api/system-resource-management/knowledge'
import documentResourceApi from '@/api/system-resource-management/document'
import paragraphResourceApi from '@/api/system-resource-management/paragraph'
import problemResourceApi from '@/api/system-resource-management/problem'
import modelResourceApi from '@/api/system-resource-management/model'
import chatUserResourceApi from '@/api/system-resource-management/chat-user'
import applicationResourceApi from '@/api/system-resource-management/application'
import applicationKeyResourceApi from '@/api/system-resource-management/application-key'
import workflowVersionResourceApi from '@/api/system-resource-management/workflow-version'
import chatLogResourceApi from '@/api/system-resource-management/chat-log'
import resourceAuthorizationResourceApi from '@/api/system-resource-management/resource-authorization'
import folderResourceApi from '@/api/system-resource-management/folder'

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
  application: applicationWorkspaceApi,
  applicationKey: applicationKeyWorkspaceApi,
  workflowVersion: workflowVersionWorkspaceApi,
  chatLog: chatLogWorkspaceApi,
  resourceAuthorization: resourceAuthorizationWorkspaceApi,
  folder: folderWorkspaceApi,
  resourceMapping: resourceMappingApi,
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
  knowledge: knowledgeResourceApi,
  document: documentResourceApi,
  paragraph: paragraphResourceApi,
  problem: problemResourceApi,
  model: modelResourceApi,
  tool: ToolResourceApi,
  chatUser: chatUserResourceApi,
  application: applicationResourceApi,
  applicationKey: applicationKeyResourceApi,
  workflowVersion: workflowVersionResourceApi,
  chatLog: chatLogResourceApi,
  resourceAuthorization: resourceAuthorizationResourceApi,
  folder: folderResourceApi,
} as any

const data = {
  systemShare: systemShareApiMap,
  workspace: workspaceApiMap,
  systemManage: systemManageApiMap,
  workspaceShare: workspaceApiMap,
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
