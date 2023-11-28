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
