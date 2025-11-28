import {Result} from '@/request/Result'
import {get, post, del, put} from '@/request/index'

const prefix = '/oss/file'
/**
 * 上传图片
 * @param 参数  file:file
 */
const postImage: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}`, data)
}

const getFile: (application_id: string, params: any) => Promise<Result<any>> = (application_id, params) => {
  return get(`/oss/get_url/${application_id}`, params)
}
export default {
  postImage,
  getFile
}
