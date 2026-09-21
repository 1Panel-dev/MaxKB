import type { Ref } from 'vue'
import type { Result } from '@/request/Result'
import { put } from '@/request/index'
import { chunkDocumentBatch } from '@/utils/chunk-document-batch'

/**
 * 顺序提交 batch_create。loading 在整批结束前保持为 true，避免分段请求之间闪动。
 * 任一分段失败即停止，由请求拦截器弹出错误。
 */
export async function putDocumentBatch(
  url: string,
  data: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> {
  const chunks = chunkDocumentBatch(data)
  if (loading) {
    loading.value = true
  }
  try {
    let merged: Result<any> | undefined
    for (const chunk of chunks) {
      const response = await put(url, chunk, {}, undefined, 1000 * 60 * 5)
      if (merged && Array.isArray(merged.data) && Array.isArray(response?.data)) {
        merged = { ...response, data: merged.data.concat(response.data) }
      } else {
        merged = response
      }
    }
    return merged as Result<any>
  } finally {
    if (loading) {
      loading.value = false
    }
  }
}
