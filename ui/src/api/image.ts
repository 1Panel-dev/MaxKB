import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'

const prefix = '/image'
/**
 * 上传图片
 * @param 参数  file:file
 */
const postImage: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}`, data)
}

export default {
  postImage
}
