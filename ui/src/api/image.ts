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

const getFile: (params: any) => Promise<Result<any>> = (params) => {
  return get(`/oss/get_url` , params)
}
export default {
  postImage,
  getFile
}
