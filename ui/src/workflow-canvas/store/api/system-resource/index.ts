import WorkspaceApi from '../workspace'
import ModelApi from '@/api/admin/system/resource-management/model'
import ToolApi from '@/api/admin/system/resource-management/tool/tool'

export default {
  ...WorkspaceApi,
  getModelListWithShared: ModelApi.getModelListWithShared,
  getModelParamsForm: ModelApi.getModelParamsForm,
  getToolById: ToolApi.getToolDetail,
}
