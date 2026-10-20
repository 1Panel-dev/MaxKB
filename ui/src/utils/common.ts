/** 公共工具：资源类型判断、标识生成、字段提取、文件地址与表头排序参数转换。 */
import { nanoid } from 'nanoid'
import { APPLICATION_TYPE, KNOWLEDGE_TYPE } from '@/api/enums'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'

/** 判断智能体类型、知识库接口类型或前端语义标识是否为工作流；空值返回 false。 */
export function isWorkFlow(type: string | number | null | undefined): boolean {
  return type === APPLICATION_TYPE.WORK_FLOW || type === KNOWLEDGE_TYPE.WORKFLOW || type === KNOWLEDGE_TYPE_KEY.WORKFLOW
}

/*
  随机id
*/
export function randomId() {
  return nanoid()
}

export const getAttrsArray = (array: Array<Record<string, unknown>>, attr: string) => {
  return array.map((item) => {
    return item[attr]
  })
}

export const downloadByURL = (url: string, name: string) => {
  const a = document.createElement('a')
  a.setAttribute('href', url)
  a.setAttribute('target', '_blank')
  a.setAttribute('download', name)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export const getFileUrl = (fileId?: string) => {
  if (fileId) {
    return `./oss/file/${fileId}`
  }
  return ''
}

/** 将表头排序转换为后端正负字段；支持字段映射，取消排序时返回 undefined。 */
export function toOrderBy(
  { prop, order }: { prop?: string; order: 'ascending' | 'descending' | null },
  mapField?: (prop: string) => string,
): string | undefined {
  if (!prop || !order) return undefined
  const field = mapField ? mapField(prop) : prop
  return order === 'ascending' ? field : `-${field}`
}
