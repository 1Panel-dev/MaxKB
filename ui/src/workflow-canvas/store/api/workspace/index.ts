import modelAPI from '@/api/admin/workspace/model/model'
import providerAPI from '@/api/admin/model-provider'
export default {
  getModelList: modelAPI.getModelList,
  getProviderList: providerAPI.getProviderList,
}
