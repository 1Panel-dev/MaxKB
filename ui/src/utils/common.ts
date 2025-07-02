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
/**
 * 拆分数组 每n个拆分为一个数组
 * @param sourceDataList 资源数据
 * @param splitNum       每多少个拆分为一个数组
 * @returns              拆分后数组
 */
export function splitArray<T>(sourceDataList: Array<T>, splitNum: number) {
  const count =
    sourceDataList.length % splitNum == 0
      ? sourceDataList.length / splitNum
      : sourceDataList.length / splitNum + 1
  const arrayList: Array<Array<T>> = []
  for (let i = 0; i < count; i++) {
    let index = i * splitNum
    const list: Array<T> = []
    let j = 0
    while (j < splitNum && index < sourceDataList.length) {
      list.push(sourceDataList[index++])
      j++
    }
    arrayList.push(list)
  }
  return arrayList
}

/**
 * 数字处理
 */
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

// 头像
export const defaultIcon = '/${window.MaxKB.prefix}/favicon.ico'
export function isAppIcon(url: string | undefined) {
  return url === defaultIcon ? '' : url
}

export function isFunction(fn: any) {
  return typeof fn === 'function'
}
