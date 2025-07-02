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
/*
树形结构转平
*/
export function TreeToFlatten(treeData: any[]) {
  return treeData.reduce((acc, node) => {
    const { children, ...rest } = node
    return [...acc, rest, ...(children ? TreeToFlatten(children) : [])]
  }, [])
}

/*
  从指定数组中过滤出对应的对象
*/
export function relatedObject(list: any, val: any, attr: string) {
  const filterData: any = list.find((item: any) => item[attr] === val)
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
      value === null || typeof value === 'undefined' || (typeof value === 'string' && !value),
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

// 对象数组去重
export function uniqueArray(array: Array<any>, key: string) {
  const map = new Map()
  return array.filter((item) => {
    return !map.has(item[key]) && map.set(item[key], 1)
  })
}
