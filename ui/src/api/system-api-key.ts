import {Result} from '@/request/Result'
import {get, post, del, put} from '@/request/index'

import {type Ref} from 'vue'

const prefix = '/system/api_key'

/**
 * API_KEY列表
 */
const getAPIKey: (loading?: Ref<boolean>) => Promise<Result<any>> = () => {
    return get(`${prefix}/`)
}

/**
 * 新增API_KEY
 */
const postAPIKey: (loading?: Ref<boolean>) => Promise<Result<any>> = (
    loading
) => {
    return post(`${prefix}/`, {}, undefined, loading)
}

/**
 * 删除API_KEY
 * @param 参数 application_id api_key_id
 */
const delAPIKey: (
    api_key_id: String,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (api_key_id, loading) => {
    return del(`${prefix}/${api_key_id}/`, undefined, undefined, loading)
}

/**
 * 修改API_KEY
 * data {
 *   is_active: boolean
 * }
 * @param api_key_id
 * @param data
 * @param loading
 */
const putAPIKey: (
    api_key_id: String,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (api_key_id, data, loading) => {
    return put(`${prefix}/${api_key_id}/`, data, undefined, loading)
}


export default {
    getAPIKey,
    postAPIKey,
    delAPIKey,
    putAPIKey
}
