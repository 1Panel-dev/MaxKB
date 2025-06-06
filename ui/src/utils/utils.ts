import { MsgError } from '@/utils/message'

export function toThousands(num: any) {
  return num?.toString().replace(/\d+/, function (n: any) {
    return n.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')
  })
}
export function numberFormat(num: number) {
  return num < 1000 ? toThousands(num) : toThousands((num / 1000).toFixed(1)) + 'k'
}

export function filesize(size: number) {
  if (!size) return ''
  /* byte */
  const num = 1024.0

  if (size < num) return size + 'B'
  if (size < Math.pow(num, 2)) return (size / num).toFixed(2) + 'K' //kb
  if (size < Math.pow(num, 3)) return (size / Math.pow(num, 2)).toFixed(2) + 'M' //M
  if (size < Math.pow(num, 4)) return (size / Math.pow(num, 3)).toFixed(2) + 'G' //G
  return (size / Math.pow(num, 4)).toFixed(2) + 'T' //T
}

/*
  随机id
*/
export const randomId = function () {
  return Math.floor(Math.random() * 10000) + ''
}

/*
  获取文件后缀
*/
export function fileType(name: string) {
  const suffix = name.split('.')
  return suffix[suffix.length - 1]
}

/*
  获得文件对应图片
*/
const typeList: any = {
  txt: ['txt', 'pdf', 'docx', 'md', 'html', 'zip', 'xlsx', 'xls', 'csv'],
  table: ['xlsx', 'xls', 'csv'],
  QA: ['xlsx', 'csv', 'xls', 'zip']
}

export function getImgUrl(name: string) {
  const list = Object.values(typeList).flat()

  const type = list.includes(fileType(name).toLowerCase()) ? fileType(name).toLowerCase() : 'unknown'
  return new URL(`../assets/fileType/${type}-icon.svg`, import.meta.url).href
}
// 是否是白名单后缀
export function isRightType(name: string, type: string) {
  return typeList[type].includes(fileType(name).toLowerCase())
}

/*
  从指定数组中过滤出对应的对象
*/
export function relatedObject(list: any, val: any, attr: string) {
  const filterData: any = list.filter((item: any) => item[attr] === val)?.[0]
  return filterData || null
}

// 排序
export function arraySort(list: Array<any>, property: any, desc?: boolean) {
  return list.sort((a: any, b: any) => {
    return desc ? b[property] - a[property] : a[property] - b[property]
  })
}

// 判断对象里所有属性全部为空
export function isAllPropertiesEmpty(obj: object) {
  return Object.values(obj).every(
    (value) =>
      value === null || typeof value === 'undefined' || (typeof value === 'string' && !value)
  )
}

// 数组对象中某一属性值的集合
export function getAttrsArray(array: Array<any>, attr: string) {
  return array.map((item) => {
    return item[attr]
  })
}

// 求和
export function getSum(array: Array<any>) {
  return array.reduce((total, item) => total + item, 0)
}

// 下载
export function downloadByURL(url: string, name: string) {
  const a = document.createElement('a')
  a.setAttribute('href', url)
  a.setAttribute('target', '_blank')
  a.setAttribute('download', name)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// 截取文件名
export function cutFilename(filename: string, num: number) {
  const lastIndex = filename.lastIndexOf('.')
  const suffix = lastIndex === -1 ? '' : filename.substring(lastIndex + 1)
  return filename.substring(0, num - suffix.length - 1) + '.' + suffix
}

export function getNormalizedUrl(url: string) {
  if (url && !url.endsWith('/') && !/\.[^/]+$/.test(url)) {
    return url + '/'
  }
  return url
}

interface LoadScriptOptions {
  jsId?: string // 自定义脚本 ID
  forceReload?: boolean // 是否强制重新加载（默认 false）
}

export const loadScript = (url: string, options: LoadScriptOptions = {}): Promise<void> => {
  const { jsId, forceReload = false } = options
  const scriptId = jsId || `script-${btoa(url).slice(0, 12)}` // 生成唯一 ID

  return new Promise((resolve, reject) => {
    // 检查是否已存在且无需强制加载
    const existingScript = document.getElementById(scriptId) as HTMLScriptElement | null
    if (existingScript && !forceReload) {
      if (existingScript.src === url) {
        existingScript.onload = () => resolve() // 复用现有脚本
        return
      }
      // URL 不同则移除旧脚本
      existingScript.parentElement?.removeChild(existingScript)
    }

    // 创建新脚本
    const script = document.createElement('script')
    script.id = scriptId
    script.src = url
    script.async = true // 明确启用异步加载

    // 成功回调
    script.onload = () => {
      resolve()
    }

    // 错误处理（兼容性增强）
    script.onerror = () => {
      reject(new Error(`Failed to load script: ${url}`))
      cleanupScript(script)
    }

    // 插入到 <head> 确保加载顺序
    document.head.appendChild(script)
  })
}

// 清理脚本（可选）
const cleanupScript = (script: HTMLScriptElement) => {
  script.onload = null
  script.onerror = null
  script.parentElement?.removeChild(script)
}
