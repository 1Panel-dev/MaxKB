interface KeyValue<K, V> {
  key: K
  value: V
}
interface Dict<V> {
  [propName: string]: V
}

interface pageRequest {
  current_page: number
  page_size: number
}

interface PageList<T> {
  current: number,
  size: number,
  total: number,
  records: T
}

export type { KeyValue, Dict, pageRequest, PageList }
