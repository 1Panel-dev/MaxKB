import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { Ref } from 'vue'
const prefix = '/display'

/**
 * 查看外观设置
 */
const getThemeInfo: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}/info`, undefined, loading)
}

/**
 * 更新外观设置
 * @param 参数
 * * formData {
 *   theme
 *   icon
 *   loginLogo
 *   loginImage
 *   title
 *   slogan
 * }
 */
const postThemeInfo: (data: any, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  data,
  loading
) => {
  return post(`${prefix}/update`, data, undefined, loading)
}

export default {
  getThemeInfo,
  postThemeInfo
}
