import { get } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

const getPortalApplicationList = (loading?: Ref<boolean>): Promise<Result<any[]>> => {
  return get('/portal/application', undefined, loading)
}

export default {
  getPortalApplicationList,
}
