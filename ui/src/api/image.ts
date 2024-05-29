import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'

const prefix = '/image'
/**
 * 上傳圖片
 * @param 參數  file:file
 */
const postImage: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}`, data)
}

export default {
  postImage
}
