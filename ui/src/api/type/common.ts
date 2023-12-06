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

export type { KeyValue, Dict, pageRequest }
