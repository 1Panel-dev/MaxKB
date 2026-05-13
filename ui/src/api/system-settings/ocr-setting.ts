import { Result } from '@/request/Result'
import { get, post, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/ocr_setting'

/**
 * 获取 OCR 设置（需 ADMIN + APPEARANCE_SETTINGS:READ）
 */
const getOcrSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 更新 OCR 设置（需 ADMIN + APPEARANCE_SETTINGS:READ+EDIT）
 */
const putOcrSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return put(`${prefix}`, data, undefined, loading)
}

/**
 * 测试 OCR 设置（不落库，仅尝试初始化对应 provider）
 */
const postTestOcrSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}`, data, undefined, loading)
}

export default {
  getOcrSetting,
  putOcrSetting,
  postTestOcrSetting,
}
