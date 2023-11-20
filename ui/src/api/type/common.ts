interface KeyValue<K, V> {
  key: K
  value: V
}
interface Dict<V> {
  [propName: string]: V
}

export type { KeyValue, Dict }
